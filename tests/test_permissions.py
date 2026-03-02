"""Tests for the Permission Model (Ticket 3 acceptance criteria)."""
from __future__ import annotations

import pytest

from able_to_answer.permissions.models import AccessLevel
from able_to_answer.permissions.repository import PermissionsRepository


@pytest.fixture()
def repo() -> PermissionsRepository:
    return PermissionsRepository()


class TestCheckAccessSystem:
    def test_system_resource_accessible_by_any_user(self, repo):
        repo.grant(
            resource_id="res-1",
            owner_id="alice",
            access_level=AccessLevel.system,
        )
        assert repo.check_access("alice", "res-1") is True
        assert repo.check_access("bob", "res-1") is True
        assert repo.check_access("unknown-user", "res-1") is True

    def test_no_permission_record_denies_access(self, repo):
        assert repo.check_access("alice", "nonexistent-resource") is False


class TestCheckAccessUser:
    def test_owner_can_access_own_resource(self, repo):
        repo.grant(
            resource_id="doc-private",
            owner_id="alice",
            access_level=AccessLevel.user,
        )
        assert repo.check_access("alice", "doc-private") is True

    def test_other_user_denied_private_resource(self, repo):
        """User B must NOT retrieve a Context Bundle containing User A's private docs."""
        repo.grant(
            resource_id="doc-private",
            owner_id="alice",
            access_level=AccessLevel.user,
        )
        assert repo.check_access("bob", "doc-private") is False

    def test_anonymous_denied_private_resource(self, repo):
        repo.grant(
            resource_id="doc-private",
            owner_id="alice",
            access_level=AccessLevel.user,
        )
        assert repo.check_access("__anonymous__", "doc-private") is False


class TestCheckAccessTeam:
    def test_team_member_can_access_team_resource(self, repo):
        repo.add_user_to_team("alice", "team-eng")
        repo.grant(
            resource_id="doc-team",
            owner_id="alice",
            access_level=AccessLevel.team,
            team_id="team-eng",
        )
        assert repo.check_access("alice", "doc-team") is True

    def test_non_member_denied_team_resource(self, repo):
        repo.add_user_to_team("alice", "team-eng")
        repo.grant(
            resource_id="doc-team",
            owner_id="alice",
            access_level=AccessLevel.team,
            team_id="team-eng",
        )
        # bob is not in team-eng
        assert repo.check_access("bob", "doc-team") is False

    def test_team_level_requires_team_id(self, repo):
        with pytest.raises(ValueError):
            repo.grant(
                resource_id="doc-team",
                owner_id="alice",
                access_level=AccessLevel.team,
                team_id=None,
            )


class TestGrantAndCount:
    def test_grant_returns_permission_record(self, repo):
        rec = repo.grant(
            resource_id="res-x",
            owner_id="alice",
            access_level=AccessLevel.system,
        )
        assert rec.permission_id
        assert rec.resource_id == "res-x"
        assert rec.owner_id == "alice"
        assert rec.access_level == AccessLevel.system
        assert rec.created_at > 0

    def test_count_increases_after_grant(self, repo):
        assert repo.count() == 0
        repo.grant(resource_id="r1", owner_id="u1", access_level=AccessLevel.system)
        repo.grant(resource_id="r2", owner_id="u1", access_level=AccessLevel.system)
        assert repo.count() == 2
