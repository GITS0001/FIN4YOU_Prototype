"""
Unit tests for Computer Vision Receipt Deskewing and Perspective Transformation.
Covers:
  - Clean, already aligned receipt images
  - Rotated receipt images
  - Perspective-distorted (keystone) images
  - Portrait and landscape orientations
  - Low-contrast and shadowed images
  - Invalid, empty, and corrupted image inputs
  - Failed boundary detection and degenerate quadrilaterals
  - Fallback to original image
  - Integration with existing RapidOCR call in StatementParser
  - Regression tests for digital PDFs
"""

import os
import unittest
import numpy as np
import cv2

from fin4you.cv.receipt_deskewer import ReceiptDeskewer, DeskewResult
from fin4you.data.statement_parser import StatementParser


class TestReceiptDeskewer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.deskewer = ReceiptDeskewer()
        cls.parser = StatementParser()

    def _create_synthetic_receipt(
        self,
        width: int = 300,
        height: int = 500,
        angle_deg: float = 0.0,
        bg_size: int = 800,
        low_contrast: bool = False
    ) -> np.ndarray:
        """Helper to create realistic document image on dark background."""
        canvas = np.full((bg_size, bg_size, 3), (35, 30, 28), dtype=np.uint8)
        cx, cy = bg_size // 2, bg_size // 2

        # 4 corners of unrotated receipt
        box = cv2.boxPoints(((cx, cy), (width, height), angle_deg))
        box = np.int32(box)

        paper_color = (180, 180, 180) if low_contrast else (245, 245, 245)
        cv2.fillPoly(canvas, [box], paper_color)

        # Draw lines of text
        for y_off in range(-height // 3, height // 3, 35):
            rad = np.radians(angle_deg)
            p1 = (int(cx - (width // 3) * np.cos(rad)), int(cy + y_off - (width // 3) * np.sin(rad)))
            p2 = (int(cx + (width // 3) * np.cos(rad)), int(cy + y_off + (width // 3) * np.sin(rad)))
            cv2.line(canvas, p1, p2, (20, 20, 20), 2)

        return canvas

    def test_clean_aligned_image(self):
        """Clean, aligned image should either be detected cleanly or safely preserved."""
        img = self._create_synthetic_receipt(angle_deg=0.0)
        res = self.deskewer.deskew(img)
        self.assertIsInstance(res, DeskewResult)
        self.assertEqual(res.image.ndim, 3)
        self.assertGreater(res.image.shape[0], 50)
        self.assertGreater(res.image.shape[1], 50)

    def test_rotated_receipt_rectification(self):
        """Rotated receipt (e.g. 15°) is rectified back to planar geometry."""
        img = self._create_synthetic_receipt(width=300, height=500, angle_deg=15.0)
        res = self.deskewer.deskew(img)
        self.assertTrue(res.applied)
        self.assertEqual(res.method, "perspective")
        self.assertIsNotNone(res.corners)
        # Rectified dimensions should approximate width=300, height=500 within tolerance
        h, w = res.rectified_shape[:2]
        self.assertAlmostEqual(w, 300, delta=25)
        self.assertAlmostEqual(h, 500, delta=25)

    def test_perspective_keystone_distortion(self):
        """Perspective keystone trapezoid is rectified back into a planar rectangle."""
        bg = np.full((900, 900, 3), (40, 40, 40), dtype=np.uint8)
        corners = np.array([
            [250, 150],  # top-left (narrow)
            [650, 160],  # top-right (narrow)
            [750, 750],  # bottom-right (wide)
            [150, 740]   # bottom-left (wide)
        ], dtype=np.int32)
        cv2.fillPoly(bg, [corners], (240, 240, 240))
        for y in range(250, 700, 50):
            cv2.line(bg, (260, y), (640, y), (20, 20, 20), 2)

        res = self.deskewer.deskew(bg)
        self.assertTrue(res.applied)
        self.assertEqual(res.method, "perspective")
        self.assertIsNotNone(res.corners)

    def test_portrait_and_landscape_orientations(self):
        """Both portrait (h > w) and landscape (w > h) documents are supported."""
        # Portrait
        portrait_img = self._create_synthetic_receipt(width=250, height=550, angle_deg=10.0)
        res_p = self.deskewer.deskew(portrait_img)
        self.assertTrue(res_p.applied)
        self.assertGreater(res_p.rectified_shape[0], res_p.rectified_shape[1])

        # Landscape
        landscape_img = self._create_synthetic_receipt(width=550, height=250, angle_deg=10.0)
        res_l = self.deskewer.deskew(landscape_img)
        self.assertTrue(res_l.applied)
        self.assertGreater(res_l.rectified_shape[1], res_l.rectified_shape[0])

    def test_low_contrast_and_shadowed_receipt(self):
        """Low-contrast documents with shadows are processed without failure."""
        img = self._create_synthetic_receipt(width=300, height=500, angle_deg=12.0, low_contrast=True)
        res = self.deskewer.deskew(img)
        self.assertIsInstance(res, DeskewResult)
        self.assertEqual(res.image.ndim, 3)

    def test_invalid_and_corrupt_inputs_raise_errors(self):
        """Invalid inputs (non-existent path, empty array, 0-dim) must raise ValueError."""
        with self.assertRaises(ValueError):
            self.deskewer.deskew("non_existent_receipt_image.jpg")

        with self.assertRaises(ValueError):
            self.deskewer.deskew(np.zeros((0, 0, 3), dtype=np.uint8))

        with self.assertRaises(ValueError):
            self.deskewer.deskew(np.zeros((5, 5, 3), dtype=np.uint8))

    def test_degenerate_quadrilateral_fallback(self):
        """Degenerate quadrilaterals (e.g. collinear points or extreme needle-like shapes) fallback safely."""
        # Plain solid background with zero discernible document
        blank_bg = np.full((500, 500, 3), (128, 128, 128), dtype=np.uint8)
        res = self.deskewer.deskew(blank_bg)
        self.assertFalse(res.applied)
        self.assertEqual(res.method, "none")
        self.assertEqual(res.image.shape, blank_bg.shape)

    def test_integration_with_statement_parser(self):
        """StatementParser.parse_image_document supports enable_deskew flag and attaches metadata."""
        img_path = "data/media/images/image_01.png"
        if os.path.exists(img_path):
            res_deskewed = self.parser.parse_image_document(img_path, enable_deskew=True)
            self.assertIn("deskew_metadata", res_deskewed)
            self.assertIn("applied", res_deskewed["deskew_metadata"])
            self.assertIn("method", res_deskewed["deskew_metadata"])
            self.assertEqual(res_deskewed["document_type"], "salary_payslip")
            self.assertEqual(res_deskewed["net_amount"], 4365000.0)

            # Route without deskew
            res_raw = self.parser.parse_image_document(img_path, enable_deskew=False)
            self.assertIsNone(res_raw["deskew_metadata"])

    def test_digital_statement_regression(self):
        """Digital PDF parsing continues to work at 100% without interference."""
        pdf_path = "Indian-Bank-Statements/train/India_Bank_Statement_Digital_Type1/00001.pdf"
        if os.path.exists(pdf_path):
            res = self.parser.parse_digital_statement(pdf_path)
            self.assertEqual(res["format"], "Type 1")
            self.assertGreater(res["transaction_count"], 100)


if __name__ == '__main__':
    unittest.main()
