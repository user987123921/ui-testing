from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Literal, Optional, Tuple

import pyautogui
from loguru import logger


ActionType = Literal[
    "move",
    "click",
    "double_click",
    "right_click",
    "type",
    "key_combo",
    "scroll",
    "wait",
    "done",
]


@dataclass
class PlannedAction:
    type: ActionType
    target_detection_id: Optional[int] = None
    position_xy: Optional[Tuple[int, int]] = None
    text: Optional[str] = None
    keys: Optional[List[str]] = None
    scroll_y: Optional[int] = None
    seconds: Optional[float] = None


def _centroid(x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int]:
    return int((x1 + x2) / 2), int((y1 + y2) / 2)


def execute_actions(
    actions: List[PlannedAction],
    detections_index: dict[int, Tuple[int, int, int, int]],
    monitor_offset_xy: Tuple[int, int],
    move_duration: float = 0.15,
) -> bool:
    all_done = False
    for action in actions:
        if action.type == "done":
            logger.info("Received done action; stopping iteration loop")
            all_done = True
            continue

        target_xy: Optional[Tuple[int, int]] = None
        if action.target_detection_id is not None and action.target_detection_id in detections_index:
            x1, y1, x2, y2 = detections_index[action.target_detection_id]
            cx, cy = _centroid(x1, y1, x2, y2)
            target_xy = (cx + monitor_offset_xy[0], cy + monitor_offset_xy[1])
        elif action.position_xy is not None:
            target_xy = (action.position_xy[0] + monitor_offset_xy[0], action.position_xy[1] + monitor_offset_xy[1])

        if action.type in {"move", "click", "double_click", "right_click"} and target_xy is None:
            logger.warning(f"Action {action.type} missing target; skipping")
            continue

        if action.type == "move":
            pyautogui.moveTo(target_xy[0], target_xy[1], duration=move_duration)
        elif action.type == "click":
            pyautogui.moveTo(target_xy[0], target_xy[1], duration=move_duration)
            pyautogui.click()
        elif action.type == "double_click":
            pyautogui.moveTo(target_xy[0], target_xy[1], duration=move_duration)
            pyautogui.doubleClick()
        elif action.type == "right_click":
            pyautogui.moveTo(target_xy[0], target_xy[1], duration=move_duration)
            pyautogui.rightClick()
        elif action.type == "type":
            if action.text is None:
                logger.warning("Type action missing text; skipping")
            else:
                pyautogui.typewrite(action.text)
        elif action.type == "key_combo":
            if not action.keys:
                logger.warning("key_combo missing keys; skipping")
            else:
                pyautogui.hotkey(*action.keys)
        elif action.type == "scroll":
            amount = int(action.scroll_y or 0)
            pyautogui.scroll(amount)
        elif action.type == "wait":
            time.sleep(float(action.seconds or 0.3))
        else:
            logger.warning(f"Unknown action: {action.type}")
    return all_done

