"use strict";

const fs = require("fs");
const path = require("path");
const dotenv = require("dotenv");
dotenv.config();

const {
  createModel,
  buildInlineImagePart,
  buildFunctionResponsePart,
  extractFunctionCallsFromResponse
} = require("./gemini");

const { toolDeclarations, localToolExecutor, actionLog } = require("./tools");

function loadImageAsBase64(imagePath) {
  const abs = path.resolve(imagePath);
  const data = fs.readFileSync(abs);
  return data.toString("base64");
}

function defaultSystemInstruction() {
  return [
    "You are a precise visual testing agent working from a screenshot.",
    "- Use ONLY the provided tools to propose actions (do not narrate actions as text).",
    "- Think step-by-step and make small, safe actions.",
    "- Reference coordinates on the screenshot (pixels) when moving or clicking.",
    "- Stop when the goal is achieved or blocked and call end_test with summary and pass/fail.",
    "- Be concise."
  ].join("\n");
}

async function runVisualTest({ imagePath, goal, maxSteps = 20, modelName = "gemini-1.5-flash", debug = false }) {
  const base64 = loadImageAsBase64(imagePath);
  const mimeType = inferMimeTypeFromPath(imagePath);
  const model = createModel({
    modelName,
    functionDeclarations: toolDeclarations,
    systemInstruction: defaultSystemInstruction()
  });

  const chat = model.startChat();

  // First user message: screenshot + goal
  const initialParts = [
    { text: `Test goal: ${goal}` },
    buildInlineImagePart(mimeType, base64)
  ];

  let step = 0;
  let finished = false;
  let finalSummary = null;
  let finalPassed = null;
  let finalIssues = [];

  let response = await chat.sendMessage(initialParts);
  while (step < maxSteps && !finished) {
    step += 1;
    if (debug) {
      const rawText = (response.candidates?.[0]?.content?.parts || []).map(p => p.text).filter(Boolean).join("\n");
      if (rawText) console.error("[model-text]", rawText);
    }

    const calls = extractFunctionCallsFromResponse(response);
    if (!calls.length) {
      // Ask the model to continue or finish
      response = await chat.sendMessage([{ text: "Please continue using tools and call end_test when done." }]);
      continue;
    }

    const toolResponses = [];
    for (const call of calls) {
      const { name, args } = call;
      if (name === "end_test") {
        const exec = await localToolExecutor[name](args);
        finished = true;
        finalSummary = args?.summary || "";
        finalPassed = !!args?.passed;
        finalIssues = Array.isArray(args?.issues) ? args.issues : [];
        toolResponses.push(buildFunctionResponsePart(name, exec));
        break;
      }

      const toolImpl = localToolExecutor[name];
      if (!toolImpl) {
        const err = { ok: false, error: `Unknown tool: ${name}` };
        toolResponses.push(buildFunctionResponsePart(name, err));
      } else {
        try {
          const exec = await toolImpl(args);
          toolResponses.push(buildFunctionResponsePart(name, exec));
        } catch (e) {
          toolResponses.push(buildFunctionResponsePart(name, { ok: false, error: String(e?.message || e) }));
        }
      }
    }

    if (!finished) {
      response = await chat.sendMessage(toolResponses);
    }
  }

  if (!finished) {
    // Force finish to prevent infinite loops
    finalSummary = finalSummary || `Stopped after ${maxSteps} steps.`;
    finalPassed = false;
    finalIssues = finalIssues.length ? finalIssues : ["Step limit reached without end_test"];
  }

  return {
    passed: finalPassed,
    summary: finalSummary,
    issues: finalIssues,
    actions: actionLog.slice()
  };
}

function inferMimeTypeFromPath(p) {
  const ext = path.extname(p).toLowerCase();
  if (ext === ".png") return "image/png";
  if (ext === ".jpg" || ext === ".jpeg") return "image/jpeg";
  if (ext === ".webp") return "image/webp";
  return "application/octet-stream";
}

module.exports = {
  runVisualTest
};

