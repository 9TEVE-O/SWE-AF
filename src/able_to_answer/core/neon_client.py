"""HTTP client for the Neon Management API v2.

Thin, dependency-free wrapper (uses only the standard-library ``urllib``
so no extra packages are needed at runtime).

Neon API reference: https://console.neon.tech/api/v2/

Usage::

    from able_to_answer.core.neon_client import NeonClient

    client = NeonClient(api_key="<NEON_API_KEY>")
    projects = client.list_projects()
    new_project = client.create_project(name="my-db")
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

_BASE_URL = "https://console.neon.tech/api/v2"


class NeonAPIError(Exception):
    """Raised when the Neon API returns an error response."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(f"Neon API error {status_code}: {message}")
        self.status_code = status_code
        self.message = message


class NeonClient:
    """Client for the Neon Management API v2.

    Args:
        api_key: Neon API key (Bearer token).  If *None*, requests are sent
                 without an ``Authorization`` header — useful in tests that
                 mock the transport.
        base_url: Override the API base URL (default:
                  ``https://console.neon.tech/api/v2``).
    """

    def __init__(
        self,
        api_key: str | None,
        base_url: str = _BASE_URL,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        h: dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self._api_key:
            h["Authorization"] = f"Bearer {self._api_key}"
        return h

    @staticmethod
    def _safe_path(path: str) -> str:
        """Validate that *path* contains only URL-safe characters.

        Raises ``ValueError`` if *path* contains characters that could be used
        for URL injection (e.g. a newline, ``..``, or an embedded scheme).
        """
        # Reject embedded schemes, double-dots, and control characters.
        if any(c in path for c in ("\n", "\r", "\0")):
            raise ValueError(f"Invalid path: {path!r}")
        if ".." in path:
            raise ValueError(f"Invalid path (directory traversal): {path!r}")
        if "://" in path:
            raise ValueError(f"Invalid path (embedded scheme): {path!r}")
        return path

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> Any:
        url = f"{self._base_url}/{self._safe_path(path).lstrip('/')}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"

        data: bytes | None = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")

        req = urllib.request.Request(
            url, data=data, method=method, headers=self._headers()
        )
        try:
            with urllib.request.urlopen(req) as resp:  # noqa: S310
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            try:
                payload = json.loads(raw)
                message = payload.get("message") or payload.get("error") or str(payload)
            except (json.JSONDecodeError, AttributeError):
                message = raw.decode("utf-8", errors="replace")
            raise NeonAPIError(exc.code, message) from exc

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    def list_projects(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> dict[str, Any]:
        """List all Neon projects.

        Returns the raw JSON response which contains ``projects`` and
        optional pagination metadata.

        Neon docs: ``GET /projects``
        """
        params: dict[str, str] = {}
        if limit is not None:
            params["limit"] = str(limit)
        if cursor is not None:
            params["cursor"] = cursor
        return self._request("GET", "/projects", params=params or None)

    def create_project(
        self,
        *,
        name: str | None = None,
        region_id: str | None = None,
        pg_version: int | None = None,
    ) -> dict[str, Any]:
        """Create a new Neon project.

        Returns the newly created project object together with its default
        branch, database, endpoint, and role (as returned by Neon).

        Neon docs: ``POST /projects``
        """
        project_spec: dict[str, Any] = {}
        if name is not None:
            project_spec["name"] = name
        if region_id is not None:
            project_spec["region_id"] = region_id
        if pg_version is not None:
            project_spec["pg_version"] = pg_version
        return self._request("POST", "/projects", body={"project": project_spec})

    def get_project(self, project_id: str) -> dict[str, Any]:
        """Get details for a single Neon project.

        Neon docs: ``GET /projects/{project_id}``
        """
        return self._request("GET", f"/projects/{project_id}")

    def delete_project(self, project_id: str) -> dict[str, Any]:
        """Delete a Neon project.

        Neon docs: ``DELETE /projects/{project_id}``
        """
        return self._request("DELETE", f"/projects/{project_id}")

    # ------------------------------------------------------------------
    # Branches
    # ------------------------------------------------------------------

    def list_branches(self, project_id: str) -> dict[str, Any]:
        """List all branches for a project.

        Neon docs: ``GET /projects/{project_id}/branches``
        """
        return self._request("GET", f"/projects/{project_id}/branches")

    # ------------------------------------------------------------------
    # Databases
    # ------------------------------------------------------------------

    def list_databases(self, project_id: str, branch_id: str) -> dict[str, Any]:
        """List all databases for a given branch.

        Neon docs: ``GET /projects/{project_id}/branches/{branch_id}/databases``
        """
        return self._request(
            "GET", f"/projects/{project_id}/branches/{branch_id}/databases"
        )

    # ------------------------------------------------------------------
    # Connection URI
    # ------------------------------------------------------------------

    def get_connection_uri(
        self,
        project_id: str,
        *,
        branch_id: str | None = None,
        endpoint_id: str | None = None,
        database_name: str | None = None,
        role_name: str | None = None,
        pooled: bool = False,
    ) -> dict[str, Any]:
        """Get a PostgreSQL connection URI for a project.

        Neon docs: ``GET /projects/{project_id}/connection_uri``
        """
        params: dict[str, str] = {}
        if branch_id is not None:
            params["branch_id"] = branch_id
        if endpoint_id is not None:
            params["endpoint_id"] = endpoint_id
        if database_name is not None:
            params["database_name"] = database_name
        if role_name is not None:
            params["role_name"] = role_name
        if pooled:
            params["pooled"] = "true"
        return self._request(
            "GET",
            f"/projects/{project_id}/connection_uri",
            params=params or None,
        )
