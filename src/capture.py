from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import mss
import numpy as np
from PIL import Image


@dataclass
class Screenshot:
    image_bgr: np.ndarray
    image_pil: Image.Image
    monitor_bbox: Tuple[int, int, int, int]  # left, top, width, height


def capture_monitor(monitor_index: int = 0) -> Screenshot:
    with mss.mss() as sct:
        monitors = sct.monitors
        if monitor_index < 0 or monitor_index >= len(monitors):
            raise ValueError(f"Invalid monitor index {monitor_index}; available: 0..{len(monitors)-1}")
        region = monitors[monitor_index]
        raw = sct.grab(region)
        image_bgra = np.array(raw)
        image_bgr = image_bgra[:, :, :3].copy()
        image_rgb = image_bgr[:, :, ::-1]
        image_pil = Image.fromarray(image_rgb)
        bbox = (region["left"], region["top"], region["width"], region["height"])  # type: ignore[index]
        return Screenshot(image_bgr=image_bgr, image_pil=image_pil, monitor_bbox=bbox)

