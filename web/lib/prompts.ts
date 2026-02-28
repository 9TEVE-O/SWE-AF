import type { GenerateRequest } from "./types";

export const SYSTEM_PROMPT = `You are an expert React developer. Generate a React application based on the user's instruction.

## Constraints

- Imports are allowed ONLY for:
  - relative files you include in the "files" array (./, ../)
  - "react"
  - "react-dom/client"
- Do NOT use any other package imports (no shadcn, no radix, no framer-motion, no lodash, etc.).
- Output must be buildable by a bundler (esbuild).
- All components must use Tailwind CSS utility classes for styling (via CDN in the preview).
- Prefer a small number of files:
  - app/generated/page.tsx (entry — always required)
  - components/* (optional reusable components)
  - lib/* (optional utilities)
- Entry file MUST use: export default function GeneratedPage() { ... }
- Do NOT use any network fetch, localStorage, or external APIs.

## Output format

Return a JSON object with a "files" array. Each element has:
  - "path": string  (e.g. "app/generated/page.tsx")
  - "content": string (full file content)

Example:
{
  "files": [
    {
      "path": "app/generated/page.tsx",
      "content": "import React from 'react';\\n\\nexport default function GeneratedPage() {\\n  return <div className=\\"p-4\\">Hello</div>;\\n}\\n"
    }
  ]
}`;

export function buildUserPrompt(req: GenerateRequest): string {
  if (req.previousCode) {
    // Iteration mode
    return `Previous code (entry file):
\`\`\`tsx
${req.previousCode}
\`\`\`

User instruction: ${req.instruction}

Keep the existing file structure. Make the smallest edits needed to satisfy the instruction.
If a build error is provided, fix it.
Return multiple files if it improves structure (e.g., components/Button.tsx).
Use relative imports between your files.`;
  }

  // Generation mode
  return `User instruction: ${req.instruction}

Generate a React application for the above.
Return multiple files if it improves structure (e.g., components/Button.tsx).
Use relative imports between your files.
Always include app/generated/page.tsx as the entry file.`;
}
