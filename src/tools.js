"use strict";

// Tool declarations for Gemini function calling and local executor implementations

const toolDeclarations = [
  {
    name: "move_cursor",
    description: "Move the mouse cursor to the given screen coordinates (pixels).",
    parameters: {
      type: "object",
      properties: {
        x: { type: "number", description: "X coordinate in pixels from left" },
        y: { type: "number", description: "Y coordinate in pixels from top" }
      },
      required: ["x", "y"]
    }
  },
  {
    name: "click",
    description: "Click at the given coordinates. If coordinates are omitted, click at current cursor position.",
    parameters: {
      type: "object",
      properties: {
        x: { type: "number", description: "X coordinate in pixels from left" },
        y: { type: "number", description: "Y coordinate in pixels from top" },
        button: {
          type: "string",
          description: "Mouse button",
          enum: ["left", "right", "middle"],
          default: "left"
        }
      }
    }
  },
  {
    name: "type_text",
    description: "Type the provided text at the current focus location.",
    parameters: {
      type: "object",
      properties: {
        text: { type: "string", description: "The text to type" }
      },
      required: ["text"]
    }
  },
  {
    name: "scroll",
    description: "Scroll by the given deltas. Positive deltaY scrolls down.",
    parameters: {
      type: "object",
      properties: {
        deltaX: { type: "number", description: "Horizontal scroll delta in pixels", default: 0 },
        deltaY: { type: "number", description: "Vertical scroll delta in pixels", default: 0 }
      }
    }
  },
  {
    name: "wait_for",
    description: "Wait for a UI condition or a fixed delay before continuing.",
    parameters: {
      type: "object",
      properties: {
        ms: { type: "number", description: "Milliseconds to wait" },
        note: { type: "string", description: "What are we waiting for?" }
      }
    }
  },
  {
    name: "end_test",
    description: "Finish the test and provide a concise summary and pass/fail status.",
    parameters: {
      type: "object",
      properties: {
        summary: { type: "string", description: "1-3 sentence summary of what happened and the result" },
        passed: { type: "boolean", description: "Did the test objective succeed?" },
        issues: { type: "array", items: { type: "string" }, description: "List of issues or blockers encountered", default: [] }
      },
      required: ["summary", "passed"]
    }
  }
];

// Simple local executor: logs and returns acknowledgements. Replace with real drivers (e.g., Playwright) as needed.
const actionLog = [];

function recordAction(action) {
  const timestamp = new Date().toISOString();
  const entry = { timestamp, ...action };
  actionLog.push(entry);
  // Keep the log from exploding in long sessions
  if (actionLog.length > 1000) actionLog.shift();
  return entry;
}

const localToolExecutor = {
  async move_cursor(args) {
    const { x, y } = args || {};
    if (typeof x !== "number" || typeof y !== "number") {
      return { ok: false, error: "x and y are required numbers" };
    }
    const entry = recordAction({ tool: "move_cursor", x, y });
    return { ok: true, entry };
  },
  async click(args) {
    const { x, y, button = "left" } = args || {};
    const entry = recordAction({ tool: "click", x, y, button });
    return { ok: true, entry };
  },
  async type_text(args) {
    const { text } = args || {};
    if (typeof text !== "string") {
      return { ok: false, error: "text is required" };
    }
    const entry = recordAction({ tool: "type_text", text });
    return { ok: true, entry };
  },
  async scroll(args) {
    const { deltaX = 0, deltaY = 0 } = args || {};
    const entry = recordAction({ tool: "scroll", deltaX, deltaY });
    return { ok: true, entry };
  },
  async wait_for(args) {
    const { ms = 500, note } = args || {};
    const entry = recordAction({ tool: "wait_for", ms, note });
    if (ms > 0) {
      await new Promise((resolve) => setTimeout(resolve, Math.min(ms, 2000)));
    }
    return { ok: true, entry };
  },
  async end_test(args) {
    const { summary, passed, issues = [] } = args || {};
    const entry = recordAction({ tool: "end_test", summary, passed, issues });
    return { ok: true, entry };
  }
};

module.exports = {
  toolDeclarations,
  localToolExecutor,
  actionLog
};

