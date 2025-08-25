from __future__ import annotations

import argparse
from loguru import logger

from src.config import load_settings
from src.orchestrator import orchestrate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="UI Autotester (YOLO + OCR + Gemini)")
    parser.add_argument("--model-path", required=True, help="Path to Ultralytics YOLO .pt model")
    parser.add_argument("--goal", required=True, help="High-level goal for the agent")
    parser.add_argument("--max-iters", type=int, default=10, help="Max iterations of plan-act loop")
    parser.add_argument("--monitor", type=int, default=0, help="Monitor index for screenshots")
    parser.add_argument("--conf-threshold", type=float, default=None, help="Detection confidence threshold")
    parser.add_argument("--eligible-classes", type=str, default=None, help="Comma-separated classes to OCR")
    parser.add_argument("--ocr-langs", type=str, default=None, help="OCR languages, comma-separated (e.g., en,fr)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = load_settings()

    conf = args.conf_threshold if args.conf_threshold is not None else settings.conf_threshold
    eligible = args.eligible_classes.split(",") if args.eligible_classes else settings.eligible_classes
    ocr_langs = args.ocr_langs.split(",") if args.ocr_langs else settings.ocr_langs

    logger.info(f"Starting with model={args.model_path}, goal='{args.goal}', iters={args.max_iters}")
    orchestrate(
        settings=settings,
        model_path=args.model_path,
        goal=args.goal,
        max_iters=args.max_iters,
        monitor_index=args.monitor,
        conf_threshold=conf,
        eligible_classes=eligible,
        ocr_langs=ocr_langs,
    )


if __name__ == "__main__":
    main()

