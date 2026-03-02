"""Permissions data models for the Context Backbone."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AccessLevel(str, Enum):
    """Hierarchical access levels for resource visibility."""

    system = "system"  # Visible to all agents system-wide
    team = "team"      # Visible to members of a specific team
    user = "user"      # Visible to a single owner only


@dataclass
class PermissionRecord:
    """A single permission entry linking a resource to an owner and access level."""

    permission_id: str
    resource_id: str
    owner_id: str          # user_id that owns / created this resource
    access_level: AccessLevel
    team_id: str | None    # populated when access_level == AccessLevel.team
    created_at: int
