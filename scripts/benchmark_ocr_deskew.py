"""
Comprehensive OCR Deskewing and Geometric Rectification Benchmark (Member 2).

Compares:
  A. Baseline: Raw Image -> RapidOCR (unmodified)
  B. Deskewed: Raw Image -> OpenCV Deskewing / Perspective Warp -> RapidOCR

Evaluates:
  - Character Error Rate (CER)
  - Word Error Rate (WER)
  - Exact match rate
  - OCR latency (ms) & deskew overhead
  - Deskew detection success rate vs fallback rate
  - Improvement / unchanged / degradation breakdown
  - Separate evaluation subsets (Clean, Rotated, Skewed, Perspective-Distorted, Shadowed)

Saves empirical benchmark findings to reports/ocr_deskew_benchmark_results.json.
"""

import os
import re
import sys
import json
import time
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Add project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fin4you.data.statement_parser import StatementParser
from fin4you.cv.receipt_deskewer import ReceiptDeskewer


def normalize_text(text: str) -> str:
    """Normalize text for consistent CER and WER calculation."""
    text = text.lower()
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'[^a-z0-9\s\.\,\-\:\/]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def levenshtein_distance(seq1: List[Any], seq2: List[Any]) -> int:
    """Levenshtein edit distance for tokens or characters."""
    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i - 1] == seq2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[m][n]


def compute_cer_wer(reference: str, hypothesis: str) -> Tuple[float, float, bool]:
    """Compute Character Error Rate (CER), Word Error Rate (WER), and exact match."""
    ref_norm = normalize_text(reference)
    hyp_norm = normalize_text(hypothesis)

    if not ref_norm and not hyp_norm:
        return 0.0, 0.0, True
    if not ref_norm:
        return 1.0, 1.0, False

    # CER (character level)
    ref_chars = list(ref_norm)
    hyp_chars = list(hyp_norm)
    char_dist = levenshtein_distance(ref_chars, hyp_chars)
    cer = min(1.0, char_dist / len(ref_chars))

    # WER (word level)
    ref_words = ref_norm.split()
    hyp_words = hyp_norm.split()
    if not ref_words:
        wer = 1.0 if hyp_words else 0.0
    else:
        word_dist = levenshtein_distance(ref_words, hyp_words)
        wer = min(1.0, word_dist / len(ref_words))

    exact = (ref_norm == hyp_norm)
    return round(cer, 4), round(wer, 4), exact


def create_skewed_test_image(
    source_img: np.ndarray,
    distortion_type: str,
    angle_deg: float = 0.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate realistic mobile camera distortions on a dark desk background:
      - 'clean': unaltered crop on background
      - 'rotated': in-plane rotation on background
      - 'perspective': keystone tilt (mobile camera viewed at an angle)
      - 'low_contrast': shadow and reduced contrast
    """
    h, w = source_img.shape[:2]
    canvas_dim = int(max(h, w) * 1.6)
    canvas = np.full((canvas_dim, canvas_dim, 3), (35, 30, 28), dtype=np.uint8) # Dark desk surface

    cx, cy = canvas_dim // 2, canvas_dim // 2
    x1, y1 = cx - w // 2, cy - h // 2
    canvas[y1:y1 + h, x1:x1 + w] = source_img

    if distortion_type == "clean":
        return canvas, source_img

    elif distortion_type == "rotated":
        m_rot = cv2.getRotationMatrix2D((cx, cy), angle_deg, 1.0)
        rotated = cv2.warpAffine(canvas, m_rot, (canvas_dim, canvas_dim), flags=cv2.INTER_CUBIC, borderValue=(35, 30, 28))
        return rotated, source_img

    elif distortion_type == "perspective":
        # Realistic keystone: mobile shot from bottom tilt
        src_pts = np.array([
            [x1, y1],
            [x1 + w, y1],
            [x1 + w, y1 + h],
            [x1, y1 + h]
        ], dtype=np.float32)

        # Distort corners: top edge shrinks, bottom edge widens
        pinch = int(w * 0.18)
        drop = int(h * 0.10)
        dst_pts = np.array([
            [x1 + pinch, y1 + drop],
            [x1 + w - pinch, y1 + drop + 10],
            [x1 + w + 20, y1 + h],
            [x1 - 20, y1 + h]
        ], dtype=np.float32)

        m_persp = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped_doc = cv2.warpPerspective(source_img, m_persp, (canvas_dim, canvas_dim), flags=cv2.INTER_CUBIC)

        mask = cv2.warpPerspective(np.full((h, w), 255, dtype=np.uint8), m_persp, (canvas_dim, canvas_dim))
        canvas[mask > 0] = warped_doc[mask > 0]
        return canvas, source_img

    elif distortion_type == "low_contrast":
        # Low contrast + gradient shadow
        faded = cv2.convertScaleAbs(source_img, alpha=0.65, beta=15)
        # Add linear shadow gradient
        shadow = np.linspace(0.6, 1.0, h)[:, None, None]
        faded = np.clip(faded * shadow, 0, 255).astype(np.uint8)
        canvas[y1:y1 + h, x1:x1 + w] = faded
        return canvas, source_img

    return canvas, source_img


def run_ocr_benchmark() -> Dict[str, Any]:
    print("=" * 80)
    print("MEMBER 2: COMPUTER VISION RECEIPT DESKEWING & OCR BENCHMARK")
    print("=" * 80)

    parser = StatementParser()
    deskewer = parser.deskewer

    # Load high-resolution reference receipts from project media
    receipt_paths = [
        "data/media/images/image_02.png",  # Rent receipt
        "data/media/images/image_07.png",  # Tax invoice token
        "data/media/images/image_01.png",  # Pay slip
        "data/media/images/image_04.png",  # Item delivery details
    ]

    # Verify existing project images
    available_receipts = [p for p in receipt_paths if os.path.exists(p)]
    if not available_receipts:
        raise FileNotFoundError("Could not find receipt images in data/media/images/")

    print(f"Loaded {len(available_receipts)} real document images from data/media/images/")

    # 1. Obtain ground-truth OCR text for clean documents
    ground_truths = {}
    print("\nExtracting baseline transcriptions for reference documents...")
    for p in available_receipts:
        res = parser.parse_image_document(p, enable_deskew=False)
        text = " ".join(res["detected_text"])
        ground_truths[p] = {
            "text": text,
            "lines_count": res["raw_lines_count"],
            "image_shape": cv2.imread(p).shape
        }
        print(f"  {os.path.basename(p)}: {res['raw_lines_count']} text lines detected.")

    # 2. Build multi-scenario test suite
    test_scenarios = [
        ("Clean Scan / Digital Receipt", "clean", 0.0),
        ("Slightly Rotated Receipt (+8°)", "rotated", 8.0),
        ("Heavily Skewed Mobile Photo (+22°)", "rotated", 22.0),
        ("Perspective Distorted Photo (Keystone)", "perspective", 0.0),
        ("Low-Light / Shadowed Receipt", "low_contrast", 0.0),
    ]

    benchmark_records = []
    category_metrics = {}

    print("\n" + "=" * 80)
    print("EXECUTING A/B BENCHMARK (Original vs Deskewed OpenCV Pipeline)")
    print("=" * 80)

    for cat_name, dist_type, angle in test_scenarios:
        cat_records = []
        print(f"\nEvaluating subset: {cat_name}...")

        for p in available_receipts:
            src_img = cv2.imread(p)
            gt_text = ground_truths[p]["text"]

            test_img, _ = create_skewed_test_image(src_img, dist_type, angle_deg=angle)

            # Route A: Original Skewed Image -> RapidOCR (Baseline)
            t0 = time.perf_counter()
            res_a = parser.parse_image_document(test_img, enable_deskew=False)
            lat_a_ms = (time.perf_counter() - t0) * 1000.0
            text_a = " ".join(res_a["detected_text"])

            # Route B: Original Skewed Image -> OpenCV Deskew -> RapidOCR (Proposed)
            t1 = time.perf_counter()
            res_b = parser.parse_image_document(test_img, enable_deskew=True)
            lat_b_ms = (time.perf_counter() - t1) * 1000.0
            text_b = " ".join(res_b["detected_text"])

            cer_a, wer_a, match_a = compute_cer_wer(gt_text, text_a)
            cer_b, wer_b, match_b = compute_cer_wer(gt_text, text_b)

            deskew_applied = res_b["deskew_metadata"].get("applied", False) if res_b.get("deskew_metadata") else False
            deskew_method = res_b["deskew_metadata"].get("method", "none") if res_b.get("deskew_metadata") else "none"

            # Determine change status
            cer_delta = cer_a - cer_b  # positive means B has lower error (improved)
            if cer_delta > 0.02:
                status = "improved"
            elif cer_delta < -0.02:
                status = "degraded"
            else:
                status = "unchanged"

            record = {
                "subset": cat_name,
                "file": os.path.basename(p),
                "baseline_cer": cer_a,
                "deskew_cer": cer_b,
                "baseline_wer": wer_a,
                "deskew_wer": wer_b,
                "baseline_lines": res_a["raw_lines_count"],
                "deskew_lines": res_b["raw_lines_count"],
                "baseline_latency_ms": round(lat_a_ms, 1),
                "deskew_latency_ms": round(lat_b_ms, 1),
                "deskew_applied": deskew_applied,
                "deskew_method": deskew_method,
                "status": status,
                "cer_improvement_pct": round(cer_delta * 100, 2)
            }
            cat_records.append(record)
            benchmark_records.append(record)

            print(f"  [{os.path.basename(p)}] Status: {status.upper()} | "
                  f"Baseline CER: {cer_a:.2f} -> Deskewed CER: {cer_b:.2f} | "
                  f"Deskew Applied: {deskew_applied} ({deskew_method}) | "
                  f"Latency: {lat_b_ms:.0f}ms")

        # Category level aggregation
        mean_cer_a = np.mean([r["baseline_cer"] for r in cat_records])
        mean_cer_b = np.mean([r["deskew_cer"] for r in cat_records])
        mean_wer_a = np.mean([r["baseline_wer"] for r in cat_records])
        mean_wer_b = np.mean([r["deskew_wer"] for r in cat_records])
        detection_rate = np.mean([1.0 if r["deskew_applied"] else 0.0 for r in cat_records]) * 100.0
        fallback_rate = 100.0 - detection_rate
        mean_lat_a = np.mean([r["baseline_latency_ms"] for r in cat_records])
        mean_lat_b = np.mean([r["deskew_latency_ms"] for r in cat_records])

        category_metrics[cat_name] = {
            "baseline_mean_cer": round(float(mean_cer_a), 4),
            "deskew_mean_cer": round(float(mean_cer_b), 4),
            "baseline_mean_wer": round(float(mean_wer_a), 4),
            "deskew_mean_wer": round(float(mean_wer_b), 4),
            "detection_rate_pct": round(float(detection_rate), 1),
            "fallback_rate_pct": round(float(fallback_rate), 1),
            "baseline_latency_ms": round(float(mean_lat_a), 1),
            "deskew_latency_ms": round(float(mean_lat_b), 1),
            "cer_relative_reduction_pct": round(float((mean_cer_a - mean_cer_b) / max(0.001, mean_cer_a) * 100.0), 2)
        }

    # 3. Overall Aggregate Statistics
    total_samples = len(benchmark_records)
    n_improved = sum(1 for r in benchmark_records if r["status"] == "improved")
    n_unchanged = sum(1 for r in benchmark_records if r["status"] == "unchanged")
    n_degraded = sum(1 for r in benchmark_records if r["status"] == "degraded")

    total_cer_a = np.mean([r["baseline_cer"] for r in benchmark_records])
    total_cer_b = np.mean([r["deskew_cer"] for r in benchmark_records])
    total_wer_a = np.mean([r["baseline_wer"] for r in benchmark_records])
    total_wer_b = np.mean([r["deskew_wer"] for r in benchmark_records])
    overall_detection_rate = np.mean([1.0 if r["deskew_applied"] else 0.0 for r in benchmark_records]) * 100.0
    overall_overhead_ms = np.mean([r["deskew_latency_ms"] - r["baseline_latency_ms"] for r in benchmark_records])

    overall_summary = {
        "total_images_tested": total_samples,
        "improved_count": n_improved,
        "improved_pct": round(n_improved / total_samples * 100.0, 1),
        "unchanged_count": n_unchanged,
        "unchanged_pct": round(n_unchanged / total_samples * 100.0, 1),
        "degraded_count": n_degraded,
        "degraded_pct": round(n_degraded / total_samples * 100.0, 1),
        "overall_baseline_cer": round(float(total_cer_a), 4),
        "overall_deskew_cer": round(float(total_cer_b), 4),
        "overall_cer_reduction_pct": round(float((total_cer_a - total_cer_b) / max(0.001, total_cer_a) * 100.0), 2),
        "overall_baseline_wer": round(float(total_wer_a), 4),
        "overall_deskew_wer": round(float(total_wer_b), 4),
        "overall_detection_rate_pct": round(float(overall_detection_rate), 1),
        "overall_fallback_rate_pct": round(float(100.0 - overall_detection_rate), 1),
        "mean_deskew_overhead_ms": round(float(overall_overhead_ms), 1)
    }

    print("\n" + "=" * 80)
    print("OCR BENCHMARK SUMMARY BY SUBSET")
    print("=" * 80)
    print(f"{'Document Subset':<38} | {'Base CER':<8} | {'Deskew CER':<10} | {'Base WER':<8} | {'Deskew WER':<10} | {'Detect%':<8}")
    print("-" * 92)
    for cat_name, m in category_metrics.items():
        print(f"{cat_name:<38} | {m['baseline_mean_cer']:<8.2f} | {m['deskew_mean_cer']:<10.2f} | {m['baseline_mean_wer']:<8.2f} | {m['deskew_mean_wer']:<10.2f} | {m['detection_rate_pct']:<8.1f}")
    print("-" * 92)

    print("\nOVERALL IMPACT:")
    print(f"  Improved:   {n_improved}/{total_samples} ({overall_summary['improved_pct']}%)")
    print(f"  Unchanged:  {n_unchanged}/{total_samples} ({overall_summary['unchanged_pct']}%)")
    print(f"  Degraded:   {n_degraded}/{total_samples} ({overall_summary['degraded_pct']}%)")
    print(f"  Overall CER Reduction: {overall_summary['overall_baseline_cer']:.3f} -> {overall_summary['overall_deskew_cer']:.3f} ({overall_summary['overall_cer_reduction_pct']}% reduction)")
    print(f"  Deskew Success Rate:   {overall_summary['overall_detection_rate_pct']}% (Fallback: {overall_summary['overall_fallback_rate_pct']}%)")
    print(f"  Mean Latency Overhead: {overall_summary['mean_deskew_overhead_ms']:+.1f}ms")

    # Persist JSON report
    out_dir = Path("reports")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "ocr_deskew_benchmark_results.json"

    final_payload = {
        "overall_summary": overall_summary,
        "category_metrics": category_metrics,
        "individual_benchmarks": benchmark_records,
        "engine_info": {
            "ocr_engine": "rapidocr-onnxruntime",
            "cv_engine": f"opencv {cv2.__version__}",
            "deskew_module": "fin4you.cv.receipt_deskewer.ReceiptDeskewer"
        }
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_payload, f, indent=2)

    print(f"\nPersisted OCR benchmark results to: {out_path}")
    return final_payload


if __name__ == '__main__':
    run_ocr_benchmark()
