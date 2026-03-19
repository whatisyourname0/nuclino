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
