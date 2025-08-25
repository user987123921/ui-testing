import argparse
import json
import os
import sys


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ai-visual-tester",
        description=(
            "AI visual testing CLI. Sends a screenshot and a goal to Gemini and "
            "prints the AI's summary and proposed UI actions (tool calls)."
        ),
    )
    parser.add_argument(
        "-i",
        "--image",
        required=True,
        help="Path to the screenshot image (png/jpg).",
    )
    parser.add_argument(
        "-g",
        "--goal",
        required=True,
        help="Goal/task for the AI to achieve in the application.",
    )
    parser.add_argument(
        "--model",
        default="gemini-1.5-flash",
        help="Gemini model name to use (default: gemini-1.5-flash).",
    )
    parser.add_argument(
        "--max-actions",
        type=int,
        default=10,
        help="Maximum number of actions the AI should propose (default: 10).",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Gemini API key. If not provided, reads GEMINI_API_KEY from env.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON only (summary and actions).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_arguments(argv if argv is not None else sys.argv[1:])

    # Import lazily so --help works without dependencies installed
    try:
        from .gemini_client import plan_actions_with_gemini
    except Exception as import_error:  # noqa: BLE001
        # If user only asked for help, argparse would have exited before this path
        sys.stderr.write(
            "Failed to load Gemini client. Ensure dependencies are installed (pip install -r requirements.txt).\n"
        )
        sys.stderr.write(f"Import error: {import_error}\n")
        return 2

    api_key = args.api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.stderr.write(
            "Missing API key. Provide --api-key or set GEMINI_API_KEY environment variable.\n"
        )
        return 2

    try:
        result = plan_actions_with_gemini(
            image_path=args.image,
            goal=args.goal,
            model_name=args.model,
            api_key=api_key,
            max_actions=args.max_actions,
        )
    except FileNotFoundError as fnf_err:
        sys.stderr.write(str(fnf_err) + "\n")
        return 2
    except Exception as err:  # noqa: BLE001
        sys.stderr.write(f"Gemini call failed: {err}\n")
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    summary = result.get("summary") or ""
    actions = result.get("actions") or []

    if summary:
        print("Summary:")
        print(summary)
        print()

    if actions:
        print("Proposed actions:")
        for index, action in enumerate(actions, start=1):
            name = action.get("name")
            args = action.get("args", {})
            # Render args as key=value pairs
            args_str = ", ".join(f"{k}={json.dumps(v, ensure_ascii=False)}" for k, v in args.items())
            print(f"  {index}. {name}({args_str})")
    else:
        print("No actions proposed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

