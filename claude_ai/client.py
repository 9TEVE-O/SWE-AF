"""Compatibility wrapper for legacy ``claude_ai.client`` imports."""

from agent_ai.client import AgentAI as ClaudeAI
from agent_ai.client import AgentAIConfig as ClaudeAIConfig

__all__ = ["ClaudeAI", "ClaudeAIConfig"]
