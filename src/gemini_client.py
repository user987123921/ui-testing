from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from loguru import logger

from .actions import PlannedAction


DEFAULT_MODEL = "gemini-1.5-pro-latest"


def configure_gemini(api_key: str) -> None:
    genai.configure(api_key=api_key)


def build_prompt(
    goal: str,
    detections: List[Dict[str, Any]],
    ocr_snippets: List[Dict[str, Any]],
    iteration_index: int,
) -> str:
    guidance = (
        "You are testing a GUI application. You receive detected UI elements with bounding boxes and OCR text. "
        "Plan concise next actions (move, click, double_click, right_click, type, key_combo, scroll, wait, done) to make progress towards the goal. "
        "Prefer referencing detections by id when possible. If necessary, you can specify pixel coordinates relative to the screenshot origin (0,0 at top-left). "
        "Return ONLY compact JSON with fields: actions: [ ... ], and optionally notes."
    )
    schema_hint = {
        "type": "object",
        "properties": {
            "actions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "target_detection_id": {"type": ["integer", "null"]},
                        "position_xy": {"type": ["array", "null"], "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
                        "text": {"type": ["string", "null"]},
                        "keys": {"type": ["array", "null"], "items": {"type": "string"}},
                        "scroll_y": {"type": ["integer", "null"]},
                        "seconds": {"type": ["number", "null"]},
                    },
                    "required": ["type"],
                },
            },
            "notes": {"type": "string"},
        },
        "required": ["actions"],
    }
    prompt = {
        "role": "user",
        "parts": [
            f"Goal: {goal}\n",
            f"Iteration: {iteration_index}\n",
            guidance + "\n",
            "Detections (id, class, conf, bbox_xyxy):\n" + json.dumps(detections, ensure_ascii=False),
            "\nOCR snippets (text, conf, bbox_xyxy):\n" + json.dumps(ocr_snippets, ensure_ascii=False),
            "\nRespond with JSON only following this JSON schema:\n" + json.dumps(schema_hint),
        ],
    }
    return json.dumps(prompt)


def request_plan(
    api_key: str,
    goal: str,
    detections: List[Dict[str, Any]],
    ocr_snippets: List[Dict[str, Any]],
    iteration_index: int,
    model_name: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    configure_gemini(api_key)
    model = genai.GenerativeModel(model_name)
    prompt_json = build_prompt(goal, detections, ocr_snippets, iteration_index)
    response = model.generate_content(prompt_json)
    text = response.text or "{}"
    try:
        parsed = _extract_json(text)
    except Exception as e:
        logger.warning(f"Failed to parse model response; returning empty plan. Error: {e}")
        parsed = {"actions": [], "notes": "parse_error"}
    return parsed


def _extract_json(text: str) -> Dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return {"actions": [], "notes": "no_json"}
    candidate = text[start : end + 1]
    data = json.loads(candidate)
    if "actions" not in data or not isinstance(data["actions"], list):
        data["actions"] = []
    return data


def convert_to_actions(plan: Dict[str, Any]) -> List[PlannedAction]:
    actions: List[PlannedAction] = []
    for item in plan.get("actions", []):
        try:
            actions.append(
                PlannedAction(
                    type=item.get("type"),
                    target_detection_id=item.get("target_detection_id"),
                    position_xy=tuple(item.get("position_xy")) if item.get("position_xy") else None,
                    text=item.get("text"),
                    keys=item.get("keys"),
                    scroll_y=item.get("scroll_y"),
                    seconds=item.get("seconds"),
                )
            )
        except Exception as e:
            logger.warning(f"Skipping invalid action: {item}. Error: {e}")
    return actions

