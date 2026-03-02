import * as esbuild from "esbuild";
import type { GeneratedFile } from "./types";

/**
 * Bundles multi-file TS/TSX into a single browser JS string.
 * Supports:
 * - relative imports among provided files
 * - "react" and "react-dom/client" via shim modules (UMD globals in iframe)
 *
 * Disallows:
 * - any other bare imports
 */
export async function bundleFilesToBrowserJs(
  files: GeneratedFile[],
  entryPath = "app/generated/page.tsx"
) {
  const fileMap = new Map<string, string>();
  for (const f of files) {
    if (!f?.path || typeof f.content !== "string") continue;
    fileMap.set(normalisePath(f.path), f.content);
  }

  const entry = normalisePath(entryPath);
  if (!fileMap.has(entry)) {
    throw new Error(`Entry file not found: ${entryPath}`);
  }

  // Basic guard: block non-allowed bare imports early with clearer errors
  for (const [path, content] of fileMap.entries()) {
    const bare = findDisallowedBareImports(content);
    if (bare.length) {
      throw new Error(
        `Disallowed bare imports in ${path}: ${bare.join(", ")}. Allowed: react, react-dom/client, and relative imports.`
      );
    }
  }

  const result = await esbuild.build({
    bundle: true,
    write: false,
    platform: "browser",
    format: "iife",
    target: "es2020",
    sourcemap: false,
    minify: false,
    entryPoints: [entry],
    plugins: [virtualFsPlugin(fileMap), reactShimsPlugin()],
    // Ensure JSX transform works even if model uses TSX across files
    jsx: "transform",
    jsxFactory: "React.createElement",
    jsxFragment: "React.Fragment",
    // Keep all code inside a single IIFE, but rely on UMD globals in iframe
    banner: {
      js: "var React = window.React;",
    },
  });

  const js = result.outputFiles?.[0]?.text;
  if (!js) throw new Error("Bundle produced no output");

  return js;
}

/**
 * Builds iframe HTML that loads React UMD + ReactDOM UMD and renders the default export from entry.
 * Contract: entry must export default a React component function.
 */
export function buildBundledPreviewHtml(bundledJs: string) {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <script src="https://cdn.tailwindcss.com"></script>
  <title>React Bundle Preview</title>
</head>
<body class="bg-neutral-950 text-neutral-50">
  <div id="root"></div>

  <!-- React UMD (MVP preview only) -->
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>

  <script>
    function showError(title, err) {
      const root = document.getElementById("root");
      if (!root) return;
      root.innerHTML =
        '<pre style="white-space:pre-wrap;padding:16px;font-family:ui-monospace, SFMono-Regular, Menlo, monospace;background:#0b0b0b;border:1px solid #333;border-radius:12px;margin:16px;color:#ffb4b4">' +
        title + "\\n" + String(err).replace(/</g,"&lt;") +
        "</pre>";
    }
    window.addEventListener("error", (e) => showError("Runtime error:", e.message || e.error || e));
  </script>

  <script>
  ${bundledJs}
  </script>

  <script>
    try {
      const React = window.React;
      const ReactDOM = window.ReactDOM;

      const App = window.__ITC_ENTRY_DEFAULT__;
      if (!App) throw new Error("Entry default export not found (window.__ITC_ENTRY_DEFAULT__).");

      const root = ReactDOM.createRoot(document.getElementById("root"));
      root.render(React.createElement(App));
      window.__ITC_RENDER_OK__ = true;
    } catch (e) {
      showError("Render error:", e && e.message ? e.message : e);
    }
  </script>
</body>
</html>`;
}

/* ---------------- Plugins ---------------- */

function virtualFsPlugin(fileMap: Map<string, string>): esbuild.Plugin {
  return {
    name: "virtual-fs",
    setup(build) {
      // Resolve relative paths inside our virtual map
      build.onResolve({ filter: /^(\.\/|\.\.\/)/ }, (args) => {
        const importer = normalisePath(args.importer || "");
        const resolved = normalisePath(resolveRelative(importer, args.path));

        // Try TS/TSX index conventions
        const candidates = [
          resolved,
          `${resolved}.ts`,
          `${resolved}.tsx`,
          `${resolved}.js`,
          `${resolved}.jsx`,
          `${resolved}/index.ts`,
          `${resolved}/index.tsx`,
          `${resolved}/index.js`,
          `${resolved}/index.jsx`,
        ];

        for (const c of candidates) {
          if (fileMap.has(c)) return { path: c, namespace: "vfs" };
        }

        return {
          errors: [
            {
              text: `Cannot resolve import "${args.path}" from "${args.importer}"`,
            },
          ],
        };
      });

      // Entry path comes in as normal path; route it to vfs
      build.onResolve({ filter: /.*/ }, (args) => {
        const p = normalisePath(args.path);
        if (fileMap.has(p)) return { path: p, namespace: "vfs" };
        return null;
      });

      build.onLoad({ filter: /.*/, namespace: "vfs" }, (args) => {
        const src = fileMap.get(normalisePath(args.path));
        if (src == null)
          return { errors: [{ text: `Missing virtual file: ${args.path}` }] };

        const loader = guessLoader(args.path);
        return { contents: src, loader };
      });
    },
  };
}

function reactShimsPlugin(): esbuild.Plugin {
  const reactShim = `
    export default window.React;
    export const useState = window.React.useState;
    export const useEffect = window.React.useEffect;
    export const useMemo = window.React.useMemo;
    export const useCallback = window.React.useCallback;
    export const useRef = window.React.useRef;
    export const useReducer = window.React.useReducer;
    export const useContext = window.React.useContext;
    export const createElement = window.React.createElement;
    export const Fragment = window.React.Fragment;
  `.trim();

  const reactDomClientShim = `
    export function createRoot(el) {
      return window.ReactDOM.createRoot(el);
    }
  `.trim();

  return {
    name: "react-shims",
    setup(build) {
      build.onResolve({ filter: /^react$/ }, () => ({
        path: "react",
        namespace: "shim",
      }));
      build.onResolve({ filter: /^react-dom\/client$/ }, () => ({
        path: "react-dom/client",
        namespace: "shim",
      }));

      build.onLoad({ filter: /^react$/, namespace: "shim" }, () => ({
        contents: reactShim,
        loader: "js",
      }));
      build.onLoad(
        { filter: /^react-dom\/client$/, namespace: "shim" },
        () => ({ contents: reactDomClientShim, loader: "js" })
      );
    },
  };
}

/* ---------------- Helpers ---------------- */

function normalisePath(p: string) {
  return p.replaceAll("\\", "/").replace(/^\/+/, "");
}

function resolveRelative(importer: string, rel: string) {
  const base = importer.includes("/")
    ? importer.split("/").slice(0, -1).join("/")
    : "";
  const joined = base ? `${base}/${rel}` : rel;
  const parts = joined.split("/");

  const out: string[] = [];
  for (const part of parts) {
    if (part === "." || part === "") continue;
    if (part === "..") out.pop();
    else out.push(part);
  }
  return out.join("/");
}

function guessLoader(path: string): esbuild.Loader {
  if (path.endsWith(".tsx")) return "tsx";
  if (path.endsWith(".ts")) return "ts";
  if (path.endsWith(".jsx")) return "jsx";
  if (path.endsWith(".js")) return "js";
  if (path.endsWith(".css")) return "css";
  return "tsx";
}

function findDisallowedBareImports(src: string) {
  // crude but effective for MVP
  const matches = [
    ...src.matchAll(/import\s+[^'"]*['"]([^'"]+)['"]/g),
  ].map((m) => m[1]);
  const disallowed: string[] = [];
  for (const spec of matches) {
    const isRelative =
      spec.startsWith("./") || spec.startsWith("../");
    const isAllowedBare =
      spec === "react" || spec === "react-dom/client";
    if (!isRelative && !isAllowedBare) disallowed.push(spec);
  }
  return [...new Set(disallowed)];
}
