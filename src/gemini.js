"use strict";

const { GoogleGenerativeAI } = require("@google/generative-ai");

function getApiKey() {
  const key = process.env.GOOGLE_API_KEY;
  if (!key) {
    throw new Error("GOOGLE_API_KEY not set. Add it to .env or environment.");
  }
  return key;
}

function createModel({ modelName = "gemini-1.5-flash", functionDeclarations = [], systemInstruction }) {
  const genAI = new GoogleGenerativeAI(getApiKey());
  return genAI.getGenerativeModel({
    model: modelName,
    tools: [{ functionDeclarations }],
    systemInstruction
  });
}

function buildInlineImagePart(mimeType, base64Data) {
  return {
    inlineData: {
      mimeType,
      data: base64Data
    }
  };
}

function buildFunctionResponsePart(name, response) {
  return {
    functionResponse: {
      name,
      response
    }
  };
}

function extractFunctionCallsFromResponse(apiResponse) {
  const candidates = apiResponse && apiResponse.candidates;
  if (!candidates || !candidates.length) return [];
  const parts = candidates[0].content && candidates[0].content.parts;
  if (!parts) return [];
  const calls = [];
  for (const part of parts) {
    if (part.functionCall && part.functionCall.name) {
      calls.push({ name: part.functionCall.name, args: part.functionCall.args || {} });
    }
  }
  return calls;
}

module.exports = {
  createModel,
  buildInlineImagePart,
  buildFunctionResponsePart,
  extractFunctionCallsFromResponse
};

