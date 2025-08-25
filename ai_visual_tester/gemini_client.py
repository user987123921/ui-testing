from __future__ import annotations

import base64
import os
from typing import Any


def _encode_image_to_part(image_path: str) -> Any:
    """Return an image part acceptable by Gemini Python SDK.

    The SDK accepts PIL.Image.Image objects directly, but to avoid importing
    Pillow at module import time, we import lazily.
    """
    try:
        from PIL import Image
    except Exception as import_err:  # noqa: BLE001
        raise RuntimeError(
            "Pillow is required. Please install dependencies with: pip install -r requirements.txt"
        ) from import_err

    with Image.open(image_path) as img:
        # The SDK also supports directly passing the PIL image object
        return img.copy()


def _build_system_instruction(max_actions: int) -> str:
    return (
        "You are an expert UI testing agent. Given a screenshot of an application "
        "and a user goal, produce a brief high-level summary of the current state "
        "and propose up to "
        f"{max_actions}"
        " atomic UI actions using the provided tool calls only. Prefer minimal, "
        "reliable steps. Use absolute coordinates for pointing actions. Do not "
        "invent results from tools; you are only planning actions."
    )


def plan_actions_with_gemini(
    image_path: str,
    goal: str,
    model_name: str,
    api_key: str,
    max_actions: int = 10,
) -> dict[str, Any]:
    """Call Gemini with tool declarations and return summary and proposed actions.

    Returns a dict with shape: {"summary": str, "actions": [{"name": str, "args": dict}, ...]}
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Lazy import so CLI help works without deps.
    try:
        import google.generativeai as genai
    except Exception as import_err:  # noqa: BLE001
        raise RuntimeError(
            "google-generativeai is required. Please run: pip install -r requirements.txt"
        ) from import_err

    from .tools import get_tool_declarations

    image_part = _encode_image_to_part(image_path)

    genai.configure(api_key=api_key)

    tools = get_tool_declarations()
    system_instruction = _build_system_instruction(max_actions=max_actions)

    model = genai.GenerativeModel(
        model_name=model_name,
        tools=tools,
        system_instruction=system_instruction,
    )

    contents: list[Any] = [
        {
            "role": "user",
            "parts": [
                {
                    "text": (
                        "Goal: "
                        + goal
                        + "\nRespond with a brief summary first, then propose actions using tool calls."
                    )
                },
                image_part,
            ],
        }
    ]

    response = model.generate_content(
        contents,
        generation_config={
            "temperature": 0.1,
            "top_p": 0.9,
        },
    )

    # Parse response: collect text (summary) until first function call, then collect all calls
    summary_text_chunks: list[str] = []
    actions: list[dict[str, Any]] = []

    try:
        candidate = response.candidates[0]
    except Exception:  # noqa: BLE001
        # Fall back to response.text as summary
        return {"summary": getattr(response, "text", ""), "actions": []}

    parts = getattr(candidate, "content", None)
    parts = getattr(parts, "parts", []) if parts is not None else []

    seen_function_call = False
    for part in parts:
        # Text part
        text_value = getattr(part, "text", None)
        if isinstance(text_value, str) and not seen_function_call:
            summary_text_chunks.append(text_value)
            continue

        # Function call part
        function_call = getattr(part, "function_call", None)
        if function_call is not None:
            seen_function_call = True
            name = getattr(function_call, "name", None)
            args = getattr(function_call, "args", {}) or {}
            # Convert args to plain dict if it's not already
            try:
                args = dict(args)
            except Exception:  # noqa: BLE001
                pass
            if name:
                actions.append({"name": name, "args": args})

    summary = "\n".join(chunk.strip() for chunk in summary_text_chunks if chunk and chunk.strip())
    return {"summary": summary, "actions": actions}

