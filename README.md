## Visual AI UI Tester (Gemini + Tool Calls)

Run AI-driven visual tests from a screenshot and a natural language goal. The AI proposes actions as tool calls (move cursor, click, type, scroll) and ends with a concise summary via `end_test`.

### Setup

1. Install dependencies:
```bash
npm install
```

2. Set your Google API key:
```bash
cp .env.example .env
echo "GOOGLE_API_KEY=YOUR_KEY" > .env
```

### Usage

```bash
node src/cli.js --image ./example.png --goal "Open settings and verify dark mode is enabled"
```

Options:
- `--image, -i`: Path to a screenshot (`.png`, `.jpg`, `.webp`).
- `--goal, -g`: Natural language test goal.
- `--model, -m`: Gemini model (default: `gemini-1.5-flash`).
- `--max-steps, -s`: Max tool-use turns (default: 20).
- `--debug`: Print raw text parts from the model.

The CLI prints a PASS/FAIL summary, a chronological list of actions, and a final JSON object with `summary`, `passed`, `issues`, and `actions`.

### How it Works

- Tool schema is defined in `src/tools.js` and registered with Gemini's function calling.
- The runner (`src/runner.js`) sends the screenshot and goal to Gemini, then loops on function calls, executing them locally and sending structured function responses back to the model.
- The loop stops when `end_test` is called or the step limit is reached.

### Extend/Integrate

- Replace the `localToolExecutor` in `src/tools.js` with real drivers (e.g., Playwright) to perform actions in a live browser instead of logging.
- Add more tools (drag, key_press, select, etc.) by updating `toolDeclarations` and `localToolExecutor` consistently.

### Environment

Requires Node.js 18+.

# ui-testing