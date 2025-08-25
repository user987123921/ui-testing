AI Visual Tester (CLI)
======================

Command-line tool that sends a screenshot and a goal to Gemini and prints the AI's brief summary plus proposed UI actions (as tool calls like click/move/type).

Quick start
-----------

1) Install dependencies:

```bash
pip install -r requirements.txt
```

2) Set your API key (or pass with --api-key):

```bash
export GEMINI_API_KEY=your_key_here
```

3) Run:

```bash
python -m ai_visual_tester -i path/to/screenshot.png -g "Open settings and enable dark mode"
```

Options
-------

```bash
python -m ai_visual_tester --help
```

Key flags:

- `--image` / `-i`: Path to a screenshot image (png/jpg)
- `--goal` / `-g`: What you want the agent to accomplish
- `--model`: Gemini model (default: `gemini-1.5-flash`)
- `--max-actions`: Upper bound of actions to propose (default: 10)
- `--api-key`: Pass your API key directly (otherwise reads `GEMINI_API_KEY`)
- `--json`: Output machine-readable JSON (summary + actions)

Behavior
--------

- The CLI defines a set of UI action tool calls (move_cursor, click, type_text, key_press, scroll, wait, assert_text_present).
- It sends your screenshot and goal to Gemini with those tools enabled and asks for a brief summary followed by proposed actions.
- The CLI does not execute actions; it only prints what the AI proposes.

Notes
-----

- Coordinates are absolute pixels relative to the screenshot provided.
- If no actions are proposed, try adjusting the goal for clarity.
- To keep `--help` working without dependencies, heavy imports are done lazily at runtime.

# ui-testing