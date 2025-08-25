#!/usr/bin/env node
"use strict";

const yargs = require("yargs");
const { hideBin } = require("yargs/helpers");
const dotenv = require("dotenv");
dotenv.config();

const { runVisualTest } = require("./runner");

function assertArg(condition, message) {
  if (!condition) {
    console.error(message);
    process.exit(1);
  }
}

async function main() {
  const argv = yargs(hideBin(process.argv))
    .scriptName("visual-ai-test")
    .usage("$0 --image <path> --goal <text> [options]")
    .option("image", { alias: "i", type: "string", describe: "Path to screenshot image", demandOption: true })
    .option("goal", { alias: "g", type: "string", describe: "Test goal in natural language", demandOption: true })
    .option("model", { alias: "m", type: "string", describe: "Gemini model name", default: "gemini-1.5-flash" })
    .option("max-steps", { alias: "s", type: "number", describe: "Maximum tool-use turns", default: 20 })
    .option("debug", { type: "boolean", describe: "Print raw model text parts", default: false })
    .help()
    .argv;

  assertArg(process.env.GOOGLE_API_KEY, "GOOGLE_API_KEY not set. Put it in .env or environment.");

  const result = await runVisualTest({
    imagePath: argv.image,
    goal: argv.goal,
    maxSteps: argv["max-steps"],
    modelName: argv.model,
    debug: argv.debug
  });

  // Print a concise summary and structured JSON for machine use
  const header = result.passed ? "PASS" : "FAIL";
  console.log(`[${header}] ${result.summary}`);
  if (result.issues?.length) {
    console.log("Issues:");
    for (const issue of result.issues) console.log(`- ${issue}`);
  }
  console.log("Actions:");
  for (const a of result.actions) {
    console.log(`${a.timestamp} ${a.tool}` +
      (a.x !== undefined && a.y !== undefined ? ` (${a.x},${a.y})` : "") +
      (a.button ? ` [${a.button}]` : "") +
      (a.text ? ` text=${JSON.stringify(a.text)}` : "") +
      (a.deltaX !== undefined || a.deltaY !== undefined ? ` dx=${a.deltaX||0} dy=${a.deltaY||0}` : "") +
      (a.ms !== undefined ? ` wait=${a.ms}ms` : "") +
      (a.note ? ` note=${JSON.stringify(a.note)}` : "")
    );
  }

  // Also emit machine-readable result at the end
  console.log(JSON.stringify(result, null, 2));
}

main().catch((err) => {
  console.error(err?.stack || err?.message || String(err));
  process.exit(1);
});

