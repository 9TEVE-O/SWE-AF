import type { GenerateRequest, GeneratedOutput } from "./types";
import { SYSTEM_PROMPT, buildUserPrompt } from "./prompts";

const OPENAI_API_URL = "https://api.openai.com/v1/chat/completions";
const MODEL = process.env.OPENAI_MODEL ?? "gpt-4o-mini";

/** JSON Schema for structured output — ensures model returns files[]. */
const RESPONSE_SCHEMA = {
  type: "object",
  properties: {
    files: {
      type: "array",
      items: {
        type: "object",
        properties: {
          path: { type: "string" },
          content: { type: "string" },
        },
        required: ["path", "content"],
        additionalProperties: false,
      },
      minItems: 1,
    },
  },
  required: ["files"],
  additionalProperties: false,
} as const;

export async function openaiGenerate(req: GenerateRequest): Promise<GeneratedOutput> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error("OPENAI_API_KEY not set");

  const userPrompt = buildUserPrompt(req);

  const response = await fetch(OPENAI_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: MODEL,
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "user", content: userPrompt },
      ],
      response_format: {
        type: "json_schema",
        json_schema: {
          name: "generated_output",
          strict: true,
          schema: RESPONSE_SCHEMA,
        },
      },
      temperature: 0.3,
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`OpenAI API error ${response.status}: ${text}`);
  }

  const data = await response.json();
  const content = data?.choices?.[0]?.message?.content;
  if (!content) throw new Error("Empty response from OpenAI");

  let parsed: { files: Array<{ path: string; content: string }> };
  try {
    parsed = JSON.parse(content);
  } catch {
    throw new Error(`Failed to parse OpenAI response as JSON: ${content}`);
  }

  if (!Array.isArray(parsed?.files) || parsed.files.length === 0) {
    throw new Error("OpenAI response missing 'files' array");
  }

  return { files: parsed.files };
}
