import type { GeneratedFile } from "./types";

/**
 * Wraps the entry file to assign its default export to window.__ITC_ENTRY_DEFAULT__.
 * Works even with imports, because it's still TSX/ESM before bundling.
 */
export function wrapEntryForPreview(
  files: GeneratedFile[],
  entryPath = "app/generated/page.tsx"
): GeneratedFile[] {
  const out: GeneratedFile[] = files.map((f) => ({ ...f }));
  const i = out.findIndex((f) => f.path === entryPath);

  if (i === -1)
    throw new Error(`Entry file not found for wrapping: ${entryPath}`);

  const original = out[i].content;

  // If model uses "export default function X", assign it directly
  const namedFnMatch = original.match(
    /export\s+default\s+function\s+([A-Za-z0-9_]+)\s*\(/
  );
  if (namedFnMatch) {
    const name = namedFnMatch[1];
    out[i].content =
      original +
      `\n\n// Preview hook\n` +
      `window.__ITC_ENTRY_DEFAULT__ = ${name};\n`;
    return out;
  }

  // If "export default App" pattern exists:
  const defaultExportMatch = original.match(
    /export\s+default\s+([A-Za-z0-9_]+)\s*;/
  );
  if (defaultExportMatch) {
    const name = defaultExportMatch[1];
    out[i].content =
      original +
      `\n\n// Preview hook\n` +
      `window.__ITC_ENTRY_DEFAULT__ = ${name};\n`;
    return out;
  }

  // Otherwise fail with a clear instruction to the model
  throw new Error(
    `Entry must export default a named component. Use: export default function GeneratedPage() { ... }`
  );
}
