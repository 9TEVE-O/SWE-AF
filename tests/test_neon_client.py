"""Tests for NeonClient (Neon Management API v2 wrapper).

All HTTP calls are intercepted by a lightweight ``urllib.request.urlopen``
patch so no real network requests are made.
"""

from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from able_to_answer.core.neon_client import NeonAPIError, NeonClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_response(payload: dict, status: int = 200) -> MagicMock:
    """Build a mock context-manager-compatible response object."""
    body = json.dumps(payload).encode("utf-8")
    resp = MagicMock()
    resp.read.return_value = body
    resp.status = status
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def _patch_urlopen(payload: dict, status: int = 200):
    """Return a context manager that patches ``urlopen`` with *payload*."""
    return patch(
        "able_to_answer.core.neon_client.urllib.request.urlopen",
        return_value=_mock_response(payload, status),
    )


def _patch_urlopen_error(status: int, message: str):
    """Return a context manager that makes ``urlopen`` raise HTTPError."""
    import urllib.error

    err = urllib.error.HTTPError(
        url="https://example.com",
        code=status,
        msg=message,
        hdrs=MagicMock(),
        fp=BytesIO(json.dumps({"message": message}).encode()),
    )
    return patch(
        "able_to_answer.core.neon_client.urllib.request.urlopen",
        side_effect=err,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client() -> NeonClient:
    return NeonClient(api_key="test-key", base_url="https://neon.example.com/api/v2")


@pytest.fixture()
def client_no_key() -> NeonClient:
    return NeonClient(api_key=None, base_url="https://neon.example.com/api/v2")


# ---------------------------------------------------------------------------
# _headers
# ---------------------------------------------------------------------------


class TestHeaders:
    def test_includes_bearer_token_when_key_set(self, client):
        assert client._headers()["Authorization"] == "Bearer test-key"

    def test_omits_authorization_when_no_key(self, client_no_key):
        assert "Authorization" not in client_no_key._headers()

    def test_always_includes_accept_json(self, client):
        assert client._headers()["Accept"] == "application/json"


# ---------------------------------------------------------------------------
# list_projects
# ---------------------------------------------------------------------------


class TestListProjects:
    def test_returns_projects_list(self, client):
        payload = {"projects": [{"id": "proj-1", "name": "demo"}]}
        with _patch_urlopen(payload):
            result = client.list_projects()
        assert result == payload

    def test_request_uses_get_method(self, client):
        payload = {"projects": []}
        with _patch_urlopen(payload) as mock_open:
            client.list_projects()
        req = mock_open.call_args[0][0]
        assert req.get_method() == "GET"

    def test_url_contains_projects_path(self, client):
        with _patch_urlopen({"projects": []}) as mock_open:
            client.list_projects()
        req = mock_open.call_args[0][0]
        assert "/projects" in req.full_url

    def test_limit_added_to_query_string(self, client):
        with _patch_urlopen({"projects": []}) as mock_open:
            client.list_projects(limit=5)
        req = mock_open.call_args[0][0]
        assert "limit=5" in req.full_url

    def test_cursor_added_to_query_string(self, client):
        with _patch_urlopen({"projects": []}) as mock_open:
            client.list_projects(cursor="abc123")
        req = mock_open.call_args[0][0]
        assert "cursor=abc123" in req.full_url

    def test_no_params_when_not_provided(self, client):
        with _patch_urlopen({"projects": []}) as mock_open:
            client.list_projects()
        req = mock_open.call_args[0][0]
        assert "?" not in req.full_url


# ---------------------------------------------------------------------------
# create_project
# ---------------------------------------------------------------------------


class TestCreateProject:
    def test_returns_created_project(self, client):
        payload = {"project": {"id": "proj-2", "name": "new-proj"}}
        with _patch_urlopen(payload):
            result = client.create_project(name="new-proj")
        assert result == payload

    def test_request_uses_post_method(self, client):
        with _patch_urlopen({"project": {}}) as mock_open:
            client.create_project(name="x")
        req = mock_open.call_args[0][0]
        assert req.get_method() == "POST"

    def test_name_in_request_body(self, client):
        with _patch_urlopen({"project": {}}) as mock_open:
            client.create_project(name="my-project")
        req = mock_open.call_args[0][0]
        body = json.loads(req.data)
        assert body["project"]["name"] == "my-project"

    def test_region_id_in_request_body(self, client):
        with _patch_urlopen({"project": {}}) as mock_open:
            client.create_project(region_id="aws-us-east-2")
        req = mock_open.call_args[0][0]
        body = json.loads(req.data)
        assert body["project"]["region_id"] == "aws-us-east-2"

    def test_pg_version_in_request_body(self, client):
        with _patch_urlopen({"project": {}}) as mock_open:
            client.create_project(pg_version=16)
        req = mock_open.call_args[0][0]
        body = json.loads(req.data)
        assert body["project"]["pg_version"] == 16

    def test_empty_project_spec_when_no_args(self, client):
        with _patch_urlopen({"project": {}}) as mock_open:
            client.create_project()
        req = mock_open.call_args[0][0]
        body = json.loads(req.data)
        assert body["project"] == {}


# ---------------------------------------------------------------------------
# get_project
# ---------------------------------------------------------------------------


class TestGetProject:
    def test_returns_project(self, client):
        payload = {"project": {"id": "proj-1", "name": "demo"}}
        with _patch_urlopen(payload):
            result = client.get_project("proj-1")
        assert result == payload

    def test_url_contains_project_id(self, client):
        with _patch_urlopen({"project": {}}) as mock_open:
            client.get_project("proj-abc")
        req = mock_open.call_args[0][0]
        assert "proj-abc" in req.full_url


# ---------------------------------------------------------------------------
# delete_project
# ---------------------------------------------------------------------------


class TestDeleteProject:
    def test_uses_delete_method(self, client):
        with _patch_urlopen({}) as mock_open:
            client.delete_project("proj-1")
        req = mock_open.call_args[0][0]
        assert req.get_method() == "DELETE"

    def test_url_contains_project_id(self, client):
        with _patch_urlopen({}) as mock_open:
            client.delete_project("proj-xyz")
        req = mock_open.call_args[0][0]
        assert "proj-xyz" in req.full_url


# ---------------------------------------------------------------------------
# list_branches
# ---------------------------------------------------------------------------


class TestListBranches:
    def test_returns_branches(self, client):
        payload = {"branches": [{"id": "br-1"}]}
        with _patch_urlopen(payload):
            result = client.list_branches("proj-1")
        assert result == payload

    def test_url_contains_project_and_branches(self, client):
        with _patch_urlopen({"branches": []}) as mock_open:
            client.list_branches("proj-1")
        req = mock_open.call_args[0][0]
        assert "proj-1" in req.full_url
        assert "branches" in req.full_url


# ---------------------------------------------------------------------------
# list_databases
# ---------------------------------------------------------------------------


class TestListDatabases:
    def test_returns_databases(self, client):
        payload = {"databases": [{"id": 1, "name": "neondb"}]}
        with _patch_urlopen(payload):
            result = client.list_databases("proj-1", "br-1")
        assert result == payload

    def test_url_contains_all_path_segments(self, client):
        with _patch_urlopen({"databases": []}) as mock_open:
            client.list_databases("proj-1", "br-main")
        req = mock_open.call_args[0][0]
        assert "proj-1" in req.full_url
        assert "br-main" in req.full_url
        assert "databases" in req.full_url


# ---------------------------------------------------------------------------
# get_connection_uri
# ---------------------------------------------------------------------------


class TestGetConnectionUri:
    def test_returns_uri_object(self, client):
        payload = {"uri": "postgresql://user:pass@ep.neon.tech/neondb"}
        with _patch_urlopen(payload):
            result = client.get_connection_uri("proj-1")
        assert result == payload

    def test_pooled_adds_query_param(self, client):
        with _patch_urlopen({"uri": ""}) as mock_open:
            client.get_connection_uri("proj-1", pooled=True)
        req = mock_open.call_args[0][0]
        assert "pooled=true" in req.full_url

    def test_optional_params_in_query_string(self, client):
        with _patch_urlopen({"uri": ""}) as mock_open:
            client.get_connection_uri(
                "proj-1",
                branch_id="br-1",
                database_name="mydb",
                role_name="myuser",
            )
        req = mock_open.call_args[0][0]
        assert "branch_id=br-1" in req.full_url
        assert "database_name=mydb" in req.full_url
        assert "role_name=myuser" in req.full_url


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestNeonAPIError:
    def test_raises_neon_api_error_on_http_error(self, client):
        with _patch_urlopen_error(401, "authentication required"):
            with pytest.raises(NeonAPIError) as exc_info:
                client.list_projects()
        assert exc_info.value.status_code == 401

    def test_error_message_propagated(self, client):
        with _patch_urlopen_error(404, "project not found"):
            with pytest.raises(NeonAPIError) as exc_info:
                client.get_project("missing")
        assert "project not found" in exc_info.value.message

    def test_neon_api_error_str(self):
        err = NeonAPIError(503, "service unavailable")
        assert "503" in str(err)
        assert "service unavailable" in str(err)


# ---------------------------------------------------------------------------
# Path validation (_safe_path)
# ---------------------------------------------------------------------------


class TestSafePath:
    def test_valid_path_passes(self, client):
        assert client._safe_path("/projects/proj-1") == "/projects/proj-1"

    def test_newline_raises(self, client):
        with pytest.raises(ValueError):
            client._safe_path("/projects/proj-1\nX-Injected: header")

    def test_carriage_return_raises(self, client):
        with pytest.raises(ValueError):
            client._safe_path("/projects/proj-1\r")

    def test_null_byte_raises(self, client):
        with pytest.raises(ValueError):
            client._safe_path("/projects/\x00evil")

    def test_directory_traversal_raises(self, client):
        with pytest.raises(ValueError):
            client._safe_path("/projects/../etc/passwd")

    def test_embedded_scheme_raises(self, client):
        with pytest.raises(ValueError):
            client._safe_path("https://evil.example.com/steal")
