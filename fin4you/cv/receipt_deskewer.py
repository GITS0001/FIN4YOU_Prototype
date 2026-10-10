"""
Robust OpenCV Receipt Deskewing and Perspective Transformation Module.

Provides geometric normalization for mobile-phone photographs and skewed scans:
  1. Image validation and normalization
  2. Multi-scale edge & morphological boundary detection
  3. Non-degenerate convex quadrilateral corner identification
  4. Consistent corner ordering (top-left, top-right, bottom-right, bottom-left)
  5. Perspective rectification via cv2.warpPerspective()
  6. Residual text-line skew angle estimation and correction
  7. Robust fallback mechanism preventing OCR failure on unrectifiable documents
"""

import cv2
import time
import logging
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, List, Optional, Union, Dict, Any

logger = logging.getLogger("fin4you.cv.receipt_deskewer")


@dataclass
class DeskewResult:
    """
    Structured outcome of the receipt deskewing and rectification pipeline.
    """
    image: np.ndarray
    applied: bool
    method: str  # 'perspective', 'rotation', 'none'
    skew_angle_deg: float
    confidence: float
    corners: Optional[List[List[int]]]
    message: str
    processing_time_ms: float
    original_shape: Tuple[int, int, int]
    rectified_shape: Tuple[int, int, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "applied": self.applied,
            "method": self.method,
            "skew_angle_deg": round(self.skew_angle_deg, 2),
            "confidence": round(self.confidence, 4),
            "corners": self.corners,
            "message": self.message,
            "processing_time_ms": round(self.processing_time_ms, 2),
            "original_shape": list(self.original_shape),
            "rectified_shape": list(self.rectified_shape)
        }


class ReceiptDeskewer:
    """
    OpenCV-based geometric document deskewing engine.
    Rectifies mobile receipts and rotated document images before RapidOCR ingestion.
    """

    def __init__(
        self,
        min_area_fraction: float = 0.12,
        max_dimension: int = 2500,
        working_height: int = 800,
        enable_residual_rotation: bool = True,
        min_rotation_threshold_deg: float = 1.0,
        max_rotation_angle_deg: float = 45.0
    ):
        self.min_area_fraction = min_area_fraction
        self.max_dimension = max_dimension
        self.working_height = working_height
        self.enable_residual_rotation = enable_residual_rotation
        self.min_rotation_threshold_deg = min_rotation_threshold_deg
        self.max_rotation_angle_deg = max_rotation_angle_deg

    def deskew(self, image_input: Union[str, Path, np.ndarray]) -> DeskewResult:
        """
        Execute full deskewing pipeline with guaranteed fallback to original image.
        
        Args:
            image_input: File path (str/Path) or existing BGR image array (np.ndarray)
            
        Returns:
            DeskewResult containing rectified image array and audit metadata.
        """
        start_t = time.perf_counter()

        # Step 1: Input validation and normalization
        original_img, err_msg = self._validate_and_load(image_input)
        if original_img is None:
            raise ValueError(f"ReceiptDeskewer: Invalid image input — {err_msg}")

        orig_h, orig_w = original_img.shape[:2]
        orig_shape = (orig_h, orig_w, original_img.shape[2] if original_img.ndim == 3 else 1)

        try:
            # Step 2: Attempt quadrilateral perspective transformation
            quad_corners, quad_conf = self._detect_receipt_quadrilateral(original_img)

            if quad_corners is not None and self._validate_quadrilateral(quad_corners, orig_w, orig_h):
                ordered_pts = self._order_corners(quad_corners)
                warped = self._warp_perspective(original_img, ordered_pts)

                # Check if warped image is valid
                if warped is not None and warped.shape[0] > 50 and warped.shape[1] > 50:
                    final_img = warped
                    final_angle = 0.0

                    # Step 3: Check and rectify residual rotation on rectified receipt
                    if self.enable_residual_rotation:
                        rot_img, residual_angle = self._correct_residual_skew(warped)
                        if rot_img is not None:
                            final_img = rot_img
                            final_angle = residual_angle

                    elapsed_ms = (time.perf_counter() - start_t) * 1000.0
                    return DeskewResult(
                        image=final_img,
                        applied=True,
                        method="perspective",
                        skew_angle_deg=final_angle,
                        confidence=round(quad_conf, 4),
                        corners=ordered_pts.astype(int).tolist(),
                        message="Perspective rectification applied successfully",
                        processing_time_ms=elapsed_ms,
                        original_shape=orig_shape,
                        rectified_shape=final_img.shape
                    )

            # Step 4: Fallback A — Conservative rotation-only deskewing if no quad found
            if self.enable_residual_rotation:
                rot_img, skew_angle = self._correct_residual_skew(original_img)
                if rot_img is not None and abs(skew_angle) >= self.min_rotation_threshold_deg:
                    elapsed_ms = (time.perf_counter() - start_t) * 1000.0
                    return DeskewResult(
                        image=rot_img,
                        applied=True,
                        method="rotation",
                        skew_angle_deg=round(skew_angle, 2),
                        confidence=0.75,
                        corners=None,
                        message=f"In-plane rotation deskew applied ({skew_angle:+.1f}°)",
                        processing_time_ms=elapsed_ms,
                        original_shape=orig_shape,
                        rectified_shape=rot_img.shape
                    )

            # Step 5: Fallback B — Return untouched original image
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            return DeskewResult(
                image=original_img,
                applied=False,
                method="none",
                skew_angle_deg=0.0,
                confidence=1.0,
                corners=None,
                message="No reliable quadrilateral or skew detected; preserved original image",
                processing_time_ms=elapsed_ms,
                original_shape=orig_shape,
                rectified_shape=orig_shape
            )

        except Exception as ex:
            logger.warning("ReceiptDeskewer failed gracefully: %s. Reverting to original image.", ex)
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            return DeskewResult(
                image=original_img,
                applied=False,
                method="none",
                skew_angle_deg=0.0,
                confidence=0.0,
                corners=None,
                message=f"Fallback triggered due to exception: {str(ex)}",
                processing_time_ms=elapsed_ms,
                original_shape=orig_shape,
                rectified_shape=orig_shape
            )

    # -------------------------------------------------------------------------
    # Internal Image Processing Helpers
    # -------------------------------------------------------------------------

    def _validate_and_load(self, inp: Union[str, Path, np.ndarray]) -> Tuple[Optional[np.ndarray], str]:
        """Validate input types, readability, channels, and dimensions."""
        if isinstance(inp, (str, Path)):
            p = str(inp)
            if not Path(p).is_file():
                return None, f"File does not exist: {p}"
            img = cv2.imread(p)
            if img is None:
                return None, f"cv2.imread failed to decode file: {p}"
        elif isinstance(inp, np.ndarray):
            img = inp.copy()
        else:
            return None, f"Unsupported input type: {type(inp)}"

        if img.size == 0 or img.ndim < 2:
            return None, "Empty or zero-dimensional image array"

        h, w = img.shape[:2]
        if h < 20 or w < 20:
            return None, f"Image dimensions too small ({w}x{h})"

        # Convert grayscale or RGBA to BGR
        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.ndim == 3 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        elif img.ndim == 3 and img.shape[2] != 3:
            return None, f"Unsupported channel count: {img.shape[2]}"

        # Protect against excessive dimensions
        max_dim = max(h, w)
        if max_dim > self.max_dimension:
            scale = self.max_dimension / float(max_dim)
            img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

        return img, ""

    def _detect_receipt_quadrilateral(self, img: np.ndarray) -> Tuple[Optional[np.ndarray], float]:
        """
        Detect receipt boundary contour and approximate 4-corner polygon.
        Uses downscaled processing for noise robustness, then projects corners back.
        """
        h, w = img.shape[:2]
        scale = float(self.working_height) / float(h)
        work_w = int(w * scale)
        work_h = self.working_height

        work_img = cv2.resize(img, (work_w, work_h), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(work_img, cv2.COLOR_BGR2GRAY)

        # Bilateral filter to smooth texture while preserving sharp edges
        smoothed = cv2.bilateralFilter(gray, 9, 75, 75)

        # Multi-strategy edge and threshold maps
        edges_canny = cv2.Canny(smoothed, 30, 150)
        
        # Morphological closing to seal broken receipt borders
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        closed_canny = cv2.morphologyEx(edges_canny, cv2.MORPH_CLOSE, kernel)

        # Also compute Otsu adaptive threshold
        _, thresh_otsu = cv2.threshold(smoothed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        edges_otsu = cv2.Canny(thresh_otsu, 50, 150)
        closed_otsu = cv2.morphologyEx(edges_otsu, cv2.MORPH_CLOSE, kernel)

        candidates = []
        for edge_map in [closed_canny, closed_otsu]:
            cnts, _ = cv2.findContours(edge_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
            for c in cnts[:8]:
                area = cv2.contourArea(c)
                if area < (self.min_area_fraction * work_h * work_w):
                    continue
                peri = cv2.arcLength(c, True)
                for eps_factor in [0.02, 0.03, 0.04, 0.015]:
                    approx = cv2.approxPolyDP(c, eps_factor * peri, True)
                    if len(approx) == 4 and cv2.isContourConvex(approx):
                        # Calculate area coverage confidence
                        coverage = area / float(work_h * work_w)
                        candidates.append((approx.reshape(4, 2), coverage))
                        break

        if not candidates:
            return None, 0.0

        # Sort by area coverage
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_quad_scaled, best_conf = candidates[0]

        # Rescale corners back to original image coordinates
        inv_scale = 1.0 / scale
        original_corners = best_quad_scaled.astype(float) * inv_scale

        return original_corners, best_conf

    def _validate_quadrilateral(self, pts: np.ndarray, orig_w: int, orig_h: int) -> bool:
        """
        Verify that quadrilateral is non-degenerate:
          1. Convexity
          2. Area covers at least min_area_fraction of original image
          3. Interior angles are within reasonable document limits (50° to 130°)
        """
        if len(pts) != 4:
            return False

        # Area check
        area = cv2.contourArea(pts.astype(np.float32))
        total_area = float(orig_w * orig_h)
        if area < (self.min_area_fraction * total_area) or area > (0.99 * total_area):
            # If area is > 99% of total image, it's just the outer image boundary
            return False

        # Check internal angles
        ordered = self._order_corners(pts)
        for i in range(4):
            p1 = ordered[i]
            p2 = ordered[(i + 1) % 4]
            p3 = ordered[(i + 2) % 4]

            v1 = p1 - p2
            v2 = p3 - p2
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            if norm1 == 0 or norm2 == 0:
                return False

            cosine = np.dot(v1, v2) / (norm1 * norm2)
            cosine = np.clip(cosine, -1.0, 1.0)
            angle_deg = np.degrees(np.arccos(cosine))
            # Interior angle must be reasonably close to 90 degrees
            if angle_deg < 50.0 or angle_deg > 130.0:
                return False

        return True

    def _order_corners(self, pts: np.ndarray) -> np.ndarray:
        """
        Order 4 points: top-left, top-right, bottom-right, bottom-left.
        """
        rect = np.zeros((4, 2), dtype=np.float32)
        pts = pts.reshape(4, 2).astype(np.float32)

        # Sum of (x, y): top-left has smallest sum, bottom-right has largest
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        # Diff of (y - x): top-right has smallest diff, bottom-left has largest
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        return rect

    def _warp_perspective(self, img: np.ndarray, ordered_pts: np.ndarray) -> Optional[np.ndarray]:
        """
        Compute destination dimensions and warp quadrilateral to planar rectangle.
        """
        (tl, tr, br, bl) = ordered_pts

        # Width = max distance between bottom-right/bottom-left and top-right/top-left
        width_b = np.linalg.norm(br - bl)
        width_t = np.linalg.norm(tr - tl)
        max_w = int(max(width_b, width_t))

        # Height = max distance between top-right/bottom-right and top-left/bottom-left
        height_r = np.linalg.norm(tr - br)
        height_l = np.linalg.norm(tl - bl)
        max_h = int(max(height_r, height_l))

        if max_w < 30 or max_h < 30:
            return None

        # Destination coordinates
        dst = np.array([
            [0, 0],
            [max_w - 1, 0],
            [max_w - 1, max_h - 1],
            [0, max_h - 1]
        ], dtype=np.float32)

        m = cv2.getPerspectiveTransform(ordered_pts, dst)
        warped = cv2.warpPerspective(
            img, m, (max_w, max_h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        return warped

    def _correct_residual_skew(self, img: np.ndarray) -> Tuple[Optional[np.ndarray], float]:
        """
        Detect text-line orientation using Probabilistic Hough Transform and rectify rotation.
        """
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img.copy()

        # Edge detection for text lines
        edges = cv2.Canny(gray, 50, 200, apertureSize=3)
        lines = cv2.HoughLinesP(
            edges, 1, np.pi / 180.0,
            threshold=100, minLineLength=int(w * 0.15), maxLineGap=20
        )

        if lines is None or len(lines) == 0:
            return img, 0.0

        angles = []
        for line in lines:
            line_flat = np.asarray(line).ravel()
            if len(line_flat) < 4:
                continue
            x1, y1, x2, y2 = line_flat[:4]
            dx = float(x2 - x1)
            dy = float(y2 - y1)
            if dx == 0:
                continue
            angle = float(np.degrees(np.arctan2(dy, dx)))
            # Text lines are predominantly horizontal within [-45°, +45°]
            if abs(angle) <= self.max_rotation_angle_deg:
                angles.append(angle)

        if len(angles) < 5:
            return img, 0.0

        median_angle = float(np.median(angles))
        if abs(median_angle) < self.min_rotation_threshold_deg:
            return img, 0.0

        # Rotate around image center
        center = (w // 2, h // 2)
        rot_mat = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        
        # Calculate new bounding dimensions
        cos_val = abs(rot_mat[0, 0])
        sin_val = abs(rot_mat[0, 1])
        new_w = int((h * sin_val) + (w * cos_val))
        new_h = int((h * cos_val) + (w * sin_val))

        rot_mat[0, 2] += (new_w / 2) - center[0]
        rot_mat[1, 2] += (new_h / 2) - center[1]

        rotated = cv2.warpAffine(
            img, rot_mat, (new_w, new_h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        return rotated, median_angle
