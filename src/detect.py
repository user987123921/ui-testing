from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np
from loguru import logger
from ultralytics import YOLO


@dataclass
class Detection:
    id: int
    class_name: str
    confidence: float
    bbox_xyxy: Tuple[int, int, int, int]


class UltralyticsDetector:
    def __init__(self, model_path: str, device: str = "auto", conf_threshold: float = 0.25) -> None:
        self.model = YOLO(model_path)
        self.device = device
        self.conf_threshold = conf_threshold
        names = self.model.names if hasattr(self.model, "names") else None
        logger.info(f"Loaded model with classes: {names}")

    def detect(self, image_bgr: np.ndarray) -> List[Detection]:
        results = self.model.predict(source=image_bgr, conf=self.conf_threshold, device=self.device, verbose=False)
        detections: List[Detection] = []
        if not results:
            return detections
        result = results[0]
        if not hasattr(result, "boxes") or result.boxes is None or result.boxes.shape[0] == 0:
            raise RuntimeError(
                "The loaded model did not produce bounding boxes. Ensure you are using an object detection model (.pt), not a classifier."
            )
        class_names = result.names if hasattr(result, "names") and result.names is not None else self.model.names
        for det_id, (xyxy, conf, cls_idx) in enumerate(zip(result.boxes.xyxy.cpu().numpy(), result.boxes.conf.cpu().numpy(), result.boxes.cls.cpu().numpy())):
            x1, y1, x2, y2 = xyxy.astype(int).tolist()
            class_name = class_names.get(int(cls_idx), str(int(cls_idx))) if isinstance(class_names, dict) else str(int(cls_idx))
            detections.append(Detection(
                id=det_id,
                class_name=class_name,
                confidence=float(conf),
                bbox_xyxy=(x1, y1, x2, y2),
            ))
        return detections

