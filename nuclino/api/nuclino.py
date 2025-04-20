from typing import List, Optional, Union

from nuclino.api.client import Client
from nuclino.api.endpoints.file import FileEndpoints
from nuclino.api.endpoints.item import ItemEndpoints
from nuclino.api.endpoints.team import TeamEndpoints
from nuclino.api.endpoints.user import UserEndpoints
from nuclino.api.endpoints.workspace import WorkspaceEndpoints
from nuclino.api.types import BaseDeleteResponse
from nuclino.models.file import File
from nuclino.models.item import Collection, Item
from nuclino.models.team import Team
from nuclino.models.user import User
from nuclino.models.workspace import Workspace


class Nuclino(Client):
    """Main Nuclino API client that combines all endpoint implementations"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users = UserEndpoints(self)
        self.teams = TeamEndpoints(self)
        self.workspaces = WorkspaceEndpoints(self)
        self.items = ItemEndpoints(self)
        self.files = FileEndpoints(self)

    # User endpoints
    def get_user(self, user_id: str) -> User:
        """Get a user by ID"""
        return self.users.get_user(user_id)

    # Team endpoints
    def get_teams(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None
    ) -> List[Team]:
        """Get list of teams"""
        return self.teams.get_teams(limit=limit, after=after)

    def get_team(self, team_id: str) -> Team:
        """Get a team by ID"""
        return self.teams.get_team(team_id)

    # Workspace endpoints
    def get_workspaces(
        self,
        team_id: Optional[str] = None,
        limit: Optional[int] = None,
        after: Optional[str] = None
    ) -> List[Workspace]:
        """Get list of workspaces"""
        return self.workspaces.get_workspaces(team_id=team_id, limit=limit, after=after)

    def get_workspace(self, workspace_id: str) -> Workspace:
        """Get a workspace by ID"""
        return self.workspaces.get_workspace(workspace_id)

    # Item endpoints
    def get_items(
        self,
        team_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: Optional[int] = None,
        after: Optional[str] = None
    ) -> List[Union[Item, Collection]]:
        """Get list of items"""
        return self.items.get_items(
            team_id=team_id,
            workspace_id=workspace_id,
            limit=limit,
            after=after
        )

    def get_item(self, item_id: str) -> Union[Item, Collection]:
        """Get an item by ID"""
        return self.items.get_item(item_id)

    def create_item(
        self,
        workspace_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        object: str = 'item',
        title: Optional[str] = None,
        content: Optional[str] = None,
        index: Optional[int] = None
    ) -> Union[Item, Collection]:
        """Create a new item"""
        return self.items.create_item(
            workspace_id=workspace_id,
            parent_id=parent_id,
            object=object,
            title=title,
            content=content,
            index=index
        )

    def update_item(
        self,
        item_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> Union[Item, Collection]:
        """Update an item"""
        return self.items.update_item(item_id, title=title, content=content)

    def delete_item(self, item_id: str) -> BaseDeleteResponse:
        """Delete an item"""
        return self.items.delete_item(item_id)

    # Collection convenience methods
    def get_collection(self, collection_id: str) -> Collection:
        """Get a collection by ID"""
        return self.items.get_collection(collection_id)

    def create_collection(
        self,
        workspace_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        title: Optional[str] = None,
        index: Optional[int] = None
    ) -> Collection:
        """Create a new collection"""
        return self.items.create_collection(
            workspace_id=workspace_id,
            parent_id=parent_id,
            title=title,
            index=index
        )

    def update_collection(
        self,
        collection_id: str,
        title: Optional[str] = None
    ) -> Collection:
        """Update a collection"""
        return self.items.update_collection(collection_id, title=title)

    def delete_collection(self, collection_id: str) -> BaseDeleteResponse:
        """Delete a collection"""
        return self.items.delete_collection(collection_id)

    # File endpoints
    def get_file(self, file_id: str) -> File:
        """Get a file by ID"""
        return self.files.get_file(file_id) 