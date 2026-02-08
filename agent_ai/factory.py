"""Provider factory for AgentAI."""

from __future__ import annotations

from typing import TYPE_CHECKING

from agent_ai.providers.base import ProviderClient
from agent_ai.providers.claude import ClaudeProviderClient, ClaudeProviderConfig

if TYPE_CHECKING:
    from agent_ai.client import AgentAIConfig


def build_provider_client(config: "AgentAIConfig") -> ProviderClient:
    """Build the provider-specific client for the current config."""
    # Commit 1 only supports Claude; codex is added in commit 2.
    if config.provider != "claude":
        raise ValueError(f"Unsupported provider in this version: {config.provider}")

    provider_cfg = ClaudeProviderConfig(
        model=config.model,
        cwd=config.cwd,
        max_turns=config.max_turns,
        allowed_tools=list(config.allowed_tools),
        system_prompt=config.system_prompt,
        max_retries=config.max_retries,
        initial_delay=config.initial_delay,
        max_delay=config.max_delay,
        backoff_factor=config.backoff_factor,
        permission_mode=config.permission_mode,
        max_budget_usd=config.max_budget_usd,
        env=dict(config.env),
    )
    return ClaudeProviderClient(provider_cfg)
