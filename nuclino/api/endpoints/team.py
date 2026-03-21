from collections.abc import Iterator
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

    def iter_teams(
        self,
        limit: int = 100,
        after: Optional[str] = None,
    ) -> Iterator[Team]:
        seen_cursors: set[str] = set()
        next_after = after

        while True:
            page = self.get_teams(limit=limit, after=next_after)
            yield from page

            next_cursor = page.next_cursor
            if next_cursor is None and len(page) == limit:
                next_cursor = page.last_id
            if next_cursor is None or next_cursor in seen_cursors:
                return

            seen_cursors.add(next_cursor)
            next_after = next_cursor
