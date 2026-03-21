from collections.abc import Iterator
from typing import Optional, cast

from nuclino.api.client import Client
from nuclino.api.utils import validate_limit
from nuclino.models.shared import NuclinoList
from nuclino.models.workspace import Workspace


class WorkspaceEndpoints:
    """Workspace-related API endpoints."""

    def __init__(self, client: Client) -> None:
        self.client = client

    def get_workspaces(
        self,
        team_id: Optional[str] = None,
        limit: Optional[int] = None,
        after: Optional[str] = None,
    ) -> NuclinoList[Workspace]:
        params: dict[str, object] = {}
        limit = validate_limit(limit)
        if team_id is not None:
            params["teamId"] = team_id
        if limit is not None:
            params["limit"] = limit
        if after is not None:
            params["after"] = after
        return cast(NuclinoList[Workspace], self.client.get("/workspaces", params))

    def get_workspace(self, workspace_id: str) -> Workspace:
        return cast(Workspace, self.client.get(f"/workspaces/{workspace_id}"))

    def iter_workspaces(
        self,
        team_id: Optional[str] = None,
        limit: int = 100,
        after: Optional[str] = None,
    ) -> Iterator[Workspace]:
        seen_cursors: set[str] = set()
        next_after = after

        while True:
            page = self.get_workspaces(team_id=team_id, limit=limit, after=next_after)
            yield from page

            next_cursor = page.next_cursor
            if next_cursor is None and len(page) == limit:
                next_cursor = page.last_id
            if next_cursor is None or next_cursor in seen_cursors:
                return

            seen_cursors.add(next_cursor)
            next_after = next_cursor
