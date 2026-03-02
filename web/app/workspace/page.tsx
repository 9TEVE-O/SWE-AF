"use client";

import { useState } from "react";

interface GeneratedFile {
  path: string;
  content: string;
}

interface GeneratedOutput {
  files: GeneratedFile[];
  previewHtml?: string;
}

export default function WorkspacePage() {
  const [instruction, setInstruction] = useState("");
  const [generatedCode, setGeneratedCode] = useState("");
  const [previewHtml, setPreviewHtml] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleGenerate() {
    if (!instruction.trim()) return;
    setLoading(true);
    setError("");

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ instruction }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data?.error ?? `HTTP ${res.status}`);
      }

      const out: GeneratedOutput = await res.json();

      // Show combined multi-file view in the editor
      const combined = out.files
        .map((f) => `// --- ${f.path} ---\n${f.content}\n`)
        .join("\n");
      setGeneratedCode(combined);

      if (out.previewHtml) {
        setPreviewHtml(out.previewHtml);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function handleIterate() {
    if (!instruction.trim() || !generatedCode) return;
    setLoading(true);
    setError("");

    // Extract the entry file content from the combined view (first file block)
    const entryMatch = generatedCode.match(
      /\/\/ --- app\/generated\/page\.tsx ---\n([\s\S]*?)(?=\n\/\/ --- |$)/
    );
    const previousCode = entryMatch ? entryMatch[1].trim() : generatedCode;

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ instruction, previousCode }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data?.error ?? `HTTP ${res.status}`);
      }

      const out: GeneratedOutput = await res.json();

      const combined = out.files
        .map((f) => `// --- ${f.path} ---\n${f.content}\n`)
        .join("\n");
      setGeneratedCode(combined);

      if (out.previewHtml) {
        setPreviewHtml(out.previewHtml);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        fontFamily: "sans-serif",
        background: "#0a0a0a",
        color: "#fafafa",
      }}
    >
      {/* Header / Instruction bar */}
      <div
        style={{
          padding: "12px 16px",
          borderBottom: "1px solid #222",
          display: "flex",
          gap: "8px",
        }}
      >
        <input
          value={instruction}
          onChange={(e) => setInstruction(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !loading && handleGenerate()}
          placeholder="Describe the React app to generate…"
          style={{
            flex: 1,
            padding: "8px 12px",
            borderRadius: "8px",
            border: "1px solid #333",
            background: "#111",
            color: "#fafafa",
            fontSize: "14px",
          }}
        />
        <button
          onClick={handleGenerate}
          disabled={loading || !instruction.trim()}
          style={{
            padding: "8px 16px",
            borderRadius: "8px",
            border: "none",
            background: loading ? "#333" : "#6366f1",
            color: "#fff",
            cursor: loading ? "not-allowed" : "pointer",
            fontSize: "14px",
          }}
        >
          {loading ? "Generating…" : "Generate"}
        </button>
        {generatedCode && (
          <button
            onClick={handleIterate}
            disabled={loading}
            style={{
              padding: "8px 16px",
              borderRadius: "8px",
              border: "1px solid #444",
              background: "transparent",
              color: "#fafafa",
              cursor: loading ? "not-allowed" : "pointer",
              fontSize: "14px",
            }}
          >
            Iterate
          </button>
        )}
      </div>

      {error && (
        <div
          style={{
            padding: "8px 16px",
            background: "#3f0000",
            color: "#ffb4b4",
            fontSize: "13px",
          }}
        >
          {error}
        </div>
      )}

      {/* Main content: editor + preview */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Code editor (read-only combined view) */}
        <textarea
          readOnly
          value={generatedCode}
          placeholder="Generated code will appear here…"
          style={{
            flex: 1,
            padding: "16px",
            background: "#111",
            color: "#d4d4d4",
            border: "none",
            borderRight: "1px solid #222",
            fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
            fontSize: "13px",
            resize: "none",
            outline: "none",
          }}
        />

        {/* Preview iframe */}
        <div style={{ flex: 1, background: "#0a0a0a" }}>
          {previewHtml ? (
            <iframe
              srcDoc={previewHtml}
              sandbox="allow-scripts"
              style={{
                width: "100%",
                height: "100%",
                border: "none",
              }}
            />
          ) : (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                height: "100%",
                color: "#555",
                fontSize: "14px",
              }}
            >
              Preview will appear here after generation
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
