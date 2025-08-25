from __future__ import annotations

from typing import Any


def get_tool_declarations() -> list[dict[str, Any]]:
    """Return Gemini tool/function declarations for common UI actions.

    The schema follows Gemini's function declaration format.
    """
    return [
        {
            "function_declarations": [
                {
                    "name": "move_cursor",
                    "description": "Move the mouse cursor to absolute screen coordinates.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "integer", "minimum": 0},
                            "y": {"type": "integer", "minimum": 0},
                        },
                        "required": ["x", "y"],
                    },
                },
                {
                    "name": "click",
                    "description": "Click at absolute screen coordinates.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "integer", "minimum": 0},
                            "y": {"type": "integer", "minimum": 0},
                            "button": {
                                "type": "string",
                                "enum": ["left", "right", "middle"],
                                "default": "left",
                            },
                            "clicks": {"type": "integer", "minimum": 1, "default": 1},
                        },
                        "required": ["x", "y"],
                    },
                },
                {
                    "name": "drag_and_drop",
                    "description": "Drag from (start_x, start_y) and drop at (end_x, end_y).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_x": {"type": "integer", "minimum": 0},
                            "start_y": {"type": "integer", "minimum": 0},
                            "end_x": {"type": "integer", "minimum": 0},
                            "end_y": {"type": "integer", "minimum": 0},
                        },
                        "required": ["start_x", "start_y", "end_x", "end_y"],
                    },
                },
                {
                    "name": "type_text",
                    "description": "Type the given text at the current focus.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "enter": {"type": "boolean", "default": False},
                        },
                        "required": ["text"],
                    },
                },
                {
                    "name": "key_press",
                    "description": "Press a single key or a chord (e.g., CTRL+C).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keys": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Ordered list of keys to press as a chord.",
                            }
                        },
                        "required": ["keys"],
                    },
                },
                {
                    "name": "scroll",
                    "description": "Scroll vertically by a delta in pixels (positive is down).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "delta_y": {"type": "integer"},
                        },
                        "required": ["delta_y"],
                    },
                },
                {
                    "name": "wait",
                    "description": "Wait for a number of seconds to allow UI updates.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "seconds": {"type": "number", "minimum": 0},
                        },
                        "required": ["seconds"],
                    },
                },
                {
                    "name": "assert_text_present",
                    "description": "Assert that the given text should be visible on screen.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                        },
                        "required": ["text"],
                    },
                },
            ]
        }
    ]

