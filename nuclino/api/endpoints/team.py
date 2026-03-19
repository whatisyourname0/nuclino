from typing import Optional, cast

from nuclino.api.client import Client
from nuclino.api.utils import validate_limit
from nuclino.models.shared import NuclinoList
from nuclino.models.team import Team


class TeamEndpoints:
    """Team-related API endpoints."""

    def __init__(self, client: Client) -> None:
        self.client = client

    def get_teams(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None,
    ) -> NuclinoList[Team]:
        params: dict[str, object] = {}
        limit = validate_limit(limit)
        if limit is not None:
            params["limit"] = limit
        if after is not None:
            params["after"] = after
        return cast(NuclinoList[Team], self.client.get("/teams", params))

    def get_team(self, team_id: str) -> Team:
        return cast(Team, self.client.get(f"/teams/{team_id}"))
