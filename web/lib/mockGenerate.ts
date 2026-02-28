import type { GenerateRequest, GeneratedOutput } from "./types";

const MOCK_ENTRY = `import React, { useState } from "react";

export default function GeneratedPage() {
  const [count, setCount] = useState(0);
  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 flex flex-col items-center justify-center gap-6 p-8">
      <h1 className="text-3xl font-bold">Mock Preview</h1>
      <p className="text-neutral-400">No OPENAI_API_KEY set — showing placeholder.</p>
      <button
        onClick={() => setCount((c) => c + 1)}
        className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-semibold transition-colors"
      >
        Clicked {count} times
      </button>
    </div>
  );
}
`;

export function mockGenerate(_req: GenerateRequest): GeneratedOutput {
  return {
    files: [{ path: "app/generated/page.tsx", content: MOCK_ENTRY }],
  };
}
