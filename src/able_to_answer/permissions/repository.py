"""In-memory permissions repository with check_access helper."""
from __future__ import annotations

import time
import uuid

from able_to_answer.permissions.models import AccessLevel, PermissionRecord


class PermissionsRepository:
    """Thread-unsafe in-memory permission store (MVP).

    Access rules
    ------------
    - ``system`` resources   → accessible by any user.
    - ``team``   resources   → accessible by members whose ``team_id`` matches.
    - ``user``   resources   → accessible only by the resource owner.
    """

    def __init__(self) -> None:
        self._records: list[PermissionRecord] = []
        # Map user_id → set of team_ids the user belongs to
        self._user_teams: dict[str, set[str]] = {}

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def grant(
        self,
        *,
        resource_id: str,
        owner_id: str,
        access_level: AccessLevel,
        team_id: str | None = None,
    ) -> PermissionRecord:
        """Create and persist a new permission record."""
        if access_level == AccessLevel.team and not team_id:
            raise ValueError("team_id is required when access_level is 'team'")
        record = PermissionRecord(
            permission_id=str(uuid.uuid4()),
            resource_id=resource_id,
            owner_id=owner_id,
            access_level=access_level,
            team_id=team_id,
            created_at=int(time.time()),
        )
        self._records.append(record)
        return record

    def add_user_to_team(self, user_id: str, team_id: str) -> None:
        """Register a user as a member of a team."""
        self._user_teams.setdefault(user_id, set()).add(team_id)

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def check_access(self, user_id: str, resource_id: str) -> bool:
        """Return True if *user_id* is allowed to access *resource_id*.

        Resolution order:
        1. No permission record for this resource → deny.
        2. ``system`` access_level              → allow.
        3. ``user``   access_level + owner match → allow.
        4. ``team``   access_level + user in team → allow.
        5. Otherwise                             → deny.
        """
        records = [r for r in self._records if r.resource_id == resource_id]
        if not records:
            return False

        user_teams = self._user_teams.get(user_id, set())
        for rec in records:
            if rec.access_level == AccessLevel.system:
                return True
            if rec.access_level == AccessLevel.user and rec.owner_id == user_id:
                return True
            if (
                rec.access_level == AccessLevel.team
                and rec.team_id is not None
                and rec.team_id in user_teams
            ):
                return True
        return False

    def count(self) -> int:
        return len(self._records)
