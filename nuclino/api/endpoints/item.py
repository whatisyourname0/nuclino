from typing import Any, Optional, cast

from nuclino.api.client import Client
from nuclino.api.exceptions import NuclinoValidationError
from nuclino.api.types import BaseDeleteResponse
from nuclino.api.utils import validate_item_object, validate_limit, validate_parent_scope
from nuclino.models.item import Collection, Item
from nuclino.models.shared import NuclinoList


class ItemEndpoints:
    """Item and collection-related API endpoints."""

    def __init__(self, client: Client) -> None:
        self.client = client

    def get_items(
        self,
        team_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: Optional[int] = None,
        after: Optional[str] = None,
    ) -> NuclinoList[Item | Collection]:
        path = "/items"
        params: dict[str, Any] = {}

        if team_id is None and workspace_id is None:
            raise NuclinoValidationError(400, "Must specify either team_id or workspace_id")
        if team_id is not None and workspace_id is not None:
            raise NuclinoValidationError(400, "Cannot specify both team_id and workspace_id")

        limit = validate_limit(limit)
        if team_id is not None:
            params["teamId"] = team_id
        if workspace_id is not None:
            params["workspaceId"] = workspace_id
        if limit is not None:
            params["limit"] = limit
        if after is not None:
            params["after"] = after

        return cast(NuclinoList[Item | Collection], self.client.get(path, params))

    def get_item(self, item_id: str) -> Item | Collection:
        return cast(Item | Collection, self.client.get(f"/items/{item_id}"))

    def create_item(
        self,
        workspace_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        object: str = "item",
        title: Optional[str] = None,
        content: Optional[str] = None,
        index: Optional[int] = None,
    ) -> Item | Collection:
        validate_parent_scope(workspace_id, parent_id)
        validate_item_object(object)
        if index is not None and index < 0:
            raise NuclinoValidationError(400, "index must be greater than or equal to 0")

        data: dict[str, Any] = {"object": object}
        if workspace_id is not None:
            data["workspaceId"] = workspace_id
        if parent_id is not None:
            data["parentId"] = parent_id
        if title is not None:
            data["title"] = title
        if content is not None:
            data["content"] = content
        if index is not None:
            data["index"] = index

        return cast(Item | Collection, self.client.post("/items", data))

    def update_item(
        self,
        item_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
    ) -> Item | Collection:
        data: dict[str, Any] = {}
        if title is not None:
            data["title"] = title
        if content is not None:
            data["content"] = content
        return cast(Item | Collection, self.client.put(f"/items/{item_id}", data))

    def delete_item(self, item_id: str) -> BaseDeleteResponse:
        return cast(BaseDeleteResponse, self.client.delete(f"/items/{item_id}"))

    def get_collection(self, collection_id: str) -> Collection:
        return cast(Collection, self.get_item(collection_id))

    def create_collection(
        self,
        workspace_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        title: Optional[str] = None,
        index: Optional[int] = None,
    ) -> Collection:
        return cast(
            Collection,
            self.create_item(
                workspace_id=workspace_id,
                parent_id=parent_id,
                object="collection",
                title=title,
                index=index,
            ),
        )

    def update_collection(
        self,
        collection_id: str,
        title: Optional[str] = None,
    ) -> Collection:
        return cast(Collection, self.update_item(collection_id, title=title))

    def delete_collection(self, collection_id: str) -> BaseDeleteResponse:
        return self.delete_item(collection_id)
