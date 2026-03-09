from __future__ import annotations

from typing import Tuple

import cv2
import numpy as np


def _keep_largest_component(mask_u8: np.ndarray) -> np.ndarray:
    # mask_u8 is expected to be 0/255. connectedComponents treats non-zero as foreground.
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask_u8, connectivity=8
    )
    if num_labels <= 1:
        return mask_u8

    areas = stats[1:, cv2.CC_STAT_AREA]
    largest_label = int(np.argmax(areas)) + 1
    return (labels == largest_label).astype(np.uint8) * 255


def _odd_ksize(k: int) -> int:
    k = int(k)
    if k <= 1:
        return 0
    return k | 1


def find_ultrasound_bbox_temporal_clean(
    pixel_array: np.ndarray,
    pad: int = 10,
    nonzero_threshold: int = 1,
    std_blur_ksize: int = 5,
    open_ksize: int = 3,
    close_ksize: int = 0,
    keep_largest: bool = True,
) -> Tuple[int, int, int, int]:
    data = np.asarray(pixel_array)

    if data.ndim == 2:
        h, w = data.shape
        return (0, 0, w, h)

    if data.ndim == 4:
        # e.g. (frames, h, w, channels) -> (frames, h, w)
        data = data.mean(axis=-1)

    if data.ndim != 3:
        raise ValueError(f"Unsupported pixel_array shape: {data.shape}")

    num_frames, h, w = data.shape
    full_bbox = (0, 0, w, h)

    if num_frames < 2:
        return full_bbox

    data = data[::5]
    if data.shape[0] < 2:
        return full_bbox
    # -----------------------------------------------------------

    std = data.astype(np.float32, copy=False).std(axis=0)
    if float(std.max()) <= float(std.min()):
        return full_bbox

    std_u8 = cv2.normalize(std, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    if int(std_u8.max()) == 0:
        return full_bbox

    k = _odd_ksize(std_blur_ksize)
    if k:
        std_u8 = cv2.GaussianBlur(std_u8, (k, k), 0)

    t = int(np.clip(int(nonzero_threshold), 1, 255))
    _, mask = cv2.threshold(std_u8, t - 1, 255, cv2.THRESH_BINARY)

    for op, ksize in (
        (cv2.MORPH_OPEN, open_ksize),
        (cv2.MORPH_CLOSE, close_ksize),
    ):
        k = _odd_ksize(ksize)
        if k:
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
            mask = cv2.morphologyEx(mask, op, kernel, iterations=1)

    if keep_largest:
        mask = _keep_largest_component(mask)

    pts = cv2.findNonZero(mask)
    if pts is None:
        return full_bbox

    x, y, bw, bh = cv2.boundingRect(pts)

    x0 = max(0, x - pad)
    y0 = max(0, y - pad)
    x1 = min(w, x + bw + pad)
    y1 = min(h, y + bh + pad)

    return (x0, y0, x1 - x0, y1 - y0)
