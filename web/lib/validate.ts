import type { GenerateRequest } from "./types";

export function validateGenerateRequest(body: unknown): GenerateRequest {
  if (!body || typeof body !== "object") {
    throw new Error("Request body must be a JSON object.");
  }
  const b = body as Record<string, unknown>;
  if (typeof b.instruction !== "string" || !b.instruction.trim()) {
    throw new Error("'instruction' must be a non-empty string.");
  }
  return {
    instruction: b.instruction.trim(),
    previousCode: typeof b.previousCode === "string" ? b.previousCode : undefined,
  };
}
