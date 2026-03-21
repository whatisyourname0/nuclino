from collections.abc import Iterator
from typing import Optional

import requests

from nuclino.api.client import (
    BASE_URL,
    DEFAULT_REQUEST_TIMEOUT,
    DEFAULT_REQUESTS_PER_MINUTE,
    Client,
)
from nuclino.api.endpoints.file import FileEndpoints
from nuclino.api.endpoints.item import ItemEndpoints
from nuclino.api.endpoints.team import TeamEndpoints
from nuclino.api.endpoints.user import UserEndpoints
from nuclino.api.endpoints.workspace import WorkspaceEndpoints
from nuclino.api.types import BaseDeleteResponse
from nuclino.models.file import File
from nuclino.models.item import Collection, Item
from nuclino.models.shared import NuclinoList
from nuclino.models.team import Team
from nuclino.models.user import User
from nuclino.models.workspace import Workspace


class Nuclino(Client):
    """Main Nuclino API client that combines all endpoint implementations."""

    def __init__(
        self,
        api_key: str,
        base_url: str = BASE_URL,
        requests_per_minute: int = DEFAULT_REQUESTS_PER_MINUTE,
        request_timeout: float = DEFAULT_REQUEST_TIMEOUT,
        max_rate_limit_retries: int = 3,
        session: requests.Session | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            requests_per_minute=requests_per_minute,
            request_timeout=request_timeout,
            max_rate_limit_retries=max_rate_limit_retries,
            session=session,
        )
        self.users = UserEndpoints(self)
        self.teams = TeamEndpoints(self)
        self.workspaces = WorkspaceEndpoints(self)
        self.items = ItemEndpoints(self)
        self.files = FileEndpoints(self)

    def get_user(self, user_id: str) -> User:
        return self.users.get_user(user_id)

    def get_teams(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None,
    ) -> NuclinoList[Team]:
        return self.teams.get_teams(limit=limit, after=after)

    def get_team(self, team_id: str) -> Team:
        return self.teams.get_team(team_id)

    def iter_teams(
        self,
        limit: int = 100,
        after: Optional[str] = None,
    ) -> Iterator[Team]:
        return self.teams.iter_teams(limit=limit, after=after)

    def get_workspaces(
        self,
        team_id: Optional[str] = None,
        limit: Optional[int] = None,
        after: Optional[str] = None,
    ) -> NuclinoList[Workspace]:
        return self.workspaces.get_workspaces(team_id=team_id, limit=limit, after=after)

    def get_workspace(self, workspace_id: str) -> Workspace:
        return self.workspaces.get_workspace(workspace_id)

    def iter_workspaces(
        self,
        team_id: Optional[str] = None,
        limit: int = 100,
        after: Optional[str] = None,
    ) -> Iterator[Workspace]:
        return self.workspaces.iter_workspaces(team_id=team_id, limit=limit, after=after)

    def get_items(
        self,
        team_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        after: Optional[str] = None,
    ) -> NuclinoList[Item | Collection]:
        return self.items.get_items(
            team_id=team_id,
            workspace_id=workspace_id,
            search=search,
            limit=limit,
            after=after,
        )

    def get_item(self, item_id: str) -> Item | Collection:
        return self.items.get_item(item_id)

    def iter_items(
        self,
        team_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        after: Optional[str] = None,
    ) -> Iterator[Item | Collection]:
        return self.items.iter_items(
            team_id=team_id,
            workspace_id=workspace_id,
            search=search,
            limit=limit,
            after=after,
        )

    def create_item(
        self,
        workspace_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        object: str = "item",
        title: Optional[str] = None,
        content: Optional[str] = None,
        index: Optional[int] = None,
    ) -> Item | Collection:
        return self.items.create_item(
            workspace_id=workspace_id,
            parent_id=parent_id,
            object=object,
            title=title,
            content=content,
            index=index,
        )

    def update_item(
        self,
        item_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
    ) -> Item | Collection:
        return self.items.update_item(item_id, title=title, content=content)

    def delete_item(self, item_id: str) -> BaseDeleteResponse:
        return self.items.delete_item(item_id)

    def get_collection(self, collection_id: str) -> Collection:
        return self.items.get_collection(collection_id)

    def create_collection(
        self,
        workspace_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        title: Optional[str] = None,
        content: Optional[str] = None,
        index: Optional[int] = None,
    ) -> Collection:
        return self.items.create_collection(
            workspace_id=workspace_id,
            parent_id=parent_id,
            title=title,
            content=content,
            index=index,
        )

    def update_collection(
        self,
        collection_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
    ) -> Collection:
        return self.items.update_collection(collection_id, title=title, content=content)

    def delete_collection(self, collection_id: str) -> BaseDeleteResponse:
        return self.items.delete_collection(collection_id)

    def get_file(self, file_id: str) -> File:
        return self.files.get_file(file_id)
