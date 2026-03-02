import { NextResponse } from "next/server";
import { validateGenerateRequest } from "@/lib/validate";
import { mockGenerate } from "@/lib/mockGenerate";
import { openaiGenerate } from "@/lib/openai";
import { wrapEntryForPreview } from "@/lib/entryWrap";
import { bundleFilesToBrowserJs, buildBundledPreviewHtml } from "@/lib/bundleReact";
import type { GeneratedOutput } from "@/lib/types";

export const runtime = "nodejs";

// --- Simple in-memory rate limiter (MVP) ---
type Bucket = { tokens: number; lastRefillMs: number };
const buckets = new Map<string, Bucket>();
// Max requests per IP per minute — keeps costs bounded for self-hosted deploys
const TOKENS_PER_MIN = 12;
const REFILL_MS = 60_000;

function takeToken(ip: string) {
  const now = Date.now();
  const b = buckets.get(ip) ?? { tokens: TOKENS_PER_MIN, lastRefillMs: now };
  if (now - b.lastRefillMs >= REFILL_MS) {
    b.tokens = TOKENS_PER_MIN;
    b.lastRefillMs = now;
  }
  if (b.tokens <= 0) return false;
  b.tokens -= 1;
  buckets.set(ip, b);
  return true;
}

function getClientIp(req: Request) {
  const xf = req.headers.get("x-forwarded-for");
  if (xf) return xf.split(",")[0].trim();
  return "unknown";
}

function getEntryTsx(out: GeneratedOutput) {
  const f = out?.files?.find((x) => x?.path === "app/generated/page.tsx");
  return typeof f?.content === "string" ? f.content : null;
}

export async function POST(req: Request) {
  try {
    const ip = getClientIp(req);
    if (!takeToken(ip)) {
      return NextResponse.json(
        { error: "Rate limit exceeded. Try again in a minute." },
        { status: 429 }
      );
    }

    const body = await req.json();
    const parsed = validateGenerateRequest(body);

    const hasKey = !!process.env.OPENAI_API_KEY;

    let out: GeneratedOutput = hasKey
      ? await openaiGenerate(parsed)
      : mockGenerate(parsed);

    const attemptBundle = async (): Promise<GeneratedOutput> => {
      if (!out?.files?.length) throw new Error("Model response missing files[]");

      // Wrap entry to expose default export to iframe
      const wrapped = wrapEntryForPreview(out.files, "app/generated/page.tsx");

      // Bundle
      const js = await bundleFilesToBrowserJs(wrapped, "app/generated/page.tsx");

      // Preview html from bundled JS
      return { ...out, previewHtml: buildBundledPreviewHtml(js) };
    };

    try {
      out = await attemptBundle();
    } catch (bundleErr: unknown) {
      if (!hasKey) throw bundleErr;

      const msg =
        bundleErr instanceof Error ? bundleErr.message : String(bundleErr);

      const repairInstruction =
        (parsed.instruction ? parsed.instruction + "\n\n" : "") +
        `Fix build issues so bundling succeeds. Rules:
- Allowed bare imports: react, react-dom/client only
- All other imports must be relative and included in files[]
- Entry must be: export default function GeneratedPage() { ... }
Build error:
${msg}`;

      out = await openaiGenerate({
        ...parsed,
        instruction: repairInstruction,
        previousCode: getEntryTsx(out) ?? parsed.previousCode,
      });

      out = await attemptBundle();
    }

    return NextResponse.json(out, { status: 200 });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 400 });
  }
}
