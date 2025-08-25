from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
import easyocr


@dataclass
class OCRResult:
    text: str
    confidence: float
    bbox_xyxy: Tuple[int, int, int, int]


class OCRWrapper:
    def __init__(self, languages: List[str]) -> None:
        self.reader = easyocr.Reader(languages, gpu=False)

    def read_text(self, image_bgr: np.ndarray) -> List[OCRResult]:
        results = self.reader.readtext(image_bgr)
        ocr_results: List[OCRResult] = []
        for bbox, text, conf in results:
            xs = [int(x) for x, _ in bbox]
            ys = [int(y) for _, y in bbox]
            x1, x2 = min(xs), max(xs)
            y1, y2 = min(ys), max(ys)
            ocr_results.append(OCRResult(text=text, confidence=float(conf), bbox_xyxy=(x1, y1, x2, y2)))
        return ocr_results

