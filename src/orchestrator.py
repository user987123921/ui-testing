from __future__ import annotations

import time
from typing import Any, Dict, List

import numpy as np
from loguru import logger

from .actions import execute_actions
from .capture import capture_monitor
from .config import Settings
from .detect import UltralyticsDetector
from .gemini_client import convert_to_actions, request_plan
from .ocr import OCRWrapper


def orchestrate(
    settings: Settings,
    model_path: str,
    goal: str,
    max_iters: int = 10,
    monitor_index: int = 0,
    conf_threshold: float = 0.25,
    eligible_classes: List[str] | None = None,
    ocr_langs: List[str] | None = None,
) -> None:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    eligible = set((eligible_classes or settings.eligible_classes))
    langs = ocr_langs or settings.ocr_langs

    detector = UltralyticsDetector(model_path=model_path, device=settings.model_device, conf_threshold=conf_threshold)
    ocr = OCRWrapper(languages=langs)

    for i in range(max_iters):
        shot = capture_monitor(monitor_index)
        image_bgr = shot.image_bgr
        detections = detector.detect(image_bgr)

        ocr_snippets: List[Dict[str, Any]] = []
        detection_dicts: List[Dict[str, Any]] = []
        detection_bbox_index: dict[int, tuple[int, int, int, int]] = {}

        for det in detections:
            x1, y1, x2, y2 = det.bbox_xyxy
            detection_dicts.append({
                "id": det.id,
                "class": det.class_name,
                "conf": round(det.confidence, 4),
                "bbox_xyxy": det.bbox_xyxy,
            })
            detection_bbox_index[det.id] = (x1, y1, x2, y2)

            if det.class_name in eligible:
                roi = image_bgr[y1:y2, x1:x2]
                if roi.size > 0:
                    for res in ocr.read_text(roi):
                        # Convert OCR bbox from ROI to full-image coords
                        bx1, by1, bx2, by2 = res.bbox_xyxy
                        ocr_snippets.append({
                            "text": res.text,
                            "conf": round(res.confidence, 4),
                            "bbox_xyxy": (bx1 + x1, by1 + y1, bx2 + x1, by2 + y1),
                            "in_detection_id": det.id,
                        })

        plan = request_plan(
            api_key=settings.gemini_api_key,
            goal=goal,
            detections=detection_dicts,
            ocr_snippets=ocr_snippets,
            iteration_index=i,
        )
        actions = convert_to_actions(plan)
        logger.info(f"Planned actions: {actions}")

        left, top, width, height = shot.monitor_bbox
        done = execute_actions(
            actions=actions,
            detections_index=detection_bbox_index,
            monitor_offset_xy=(left, top),
        )
        if done:
            logger.info("Goal marked as done by planner; stopping.")
            break
        time.sleep(0.5)

