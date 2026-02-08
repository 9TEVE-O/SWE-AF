"""Compatibility wrapper for legacy ``claude_ai.types`` imports."""

from agent_ai.types import (  # noqa: F401
    AgentResponse as ClaudeResponse,
    Content,
    ErrorKind,
    Message,
    Metrics,
    Model,
    TextContent,
    ThinkingContent,
    Tool,
    ToolResultContent,
    ToolUseContent,
)

__all__ = [
    "ClaudeResponse",
    "Content",
    "ErrorKind",
    "Message",
    "Metrics",
    "Model",
    "TextContent",
    "ThinkingContent",
    "Tool",
    "ToolResultContent",
    "ToolUseContent",
]
