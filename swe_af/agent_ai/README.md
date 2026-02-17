# agent_ai

Provider-agnostic AI runtime for the SWE pipeline.

## Providers
- `claude`: backed by Claude Code SDK (`claude_agent_sdk`)
- `opencode`: backed by OpenCode CLI (`opencode run -m model`) for 75+ LLM providers (OpenRouter, OpenAI, Google, Anthropic)

## Selection
Set provider explicitly in pipeline config:
- `BuildConfig.ai_provider`
- `ExecutionConfig.ai_provider`

Valid values: `"claude"`, `"codex"`, `"opencode"`.

A single run should use one provider end-to-end.
