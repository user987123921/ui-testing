# UI Autotester (YOLO + OCR + Gemini)

This tool captures screenshots, detects UI objects using a trained Ultralytics YOLO `.pt` model, performs OCR on eligible detections, asks Gemini to plan actions, executes them (move, click, type, etc.), and repeats.

## Quick start

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment:

```bash
cp .env.example .env
``` 
Set `GEMINI_API_KEY` in `.env`.

3. Run:

```bash
python main.py \
  --model-path /absolute/path/to/your_model.pt \
  --goal "Open settings and toggle dark mode" \
  --max-iters 10
```

## CLI

```bash
python main.py --help
```

Key options:
- `--model-path`: path to Ultralytics YOLO `.pt` model
- `--eligible-classes`: comma-separated class names eligible for OCR
- `--conf-threshold`: minimum detection confidence (default 0.25)
- `--goal`: high-level task for Gemini
- `--max-iters`: number of plan-act iterations
- `--monitor`: monitor index for screenshot (default 0)
- `--ocr-langs`: OCR languages (comma-separated, default: en)

## Notes

- Requires a desktop session to capture screenshots and send mouse/keyboard input.
- On Linux servers, ensure you have access to a display (`DISPLAY` env), or run within a desktop session.

# ui-testing