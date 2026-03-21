from __future__ import annotations

from typing import Any, cast

from nuclino.api.client import Client
from nuclino.models.file import File, FileProps
from nuclino.models.item import Collection, CollectionProps, Item, ItemProps
from nuclino.models.shared import NuclinoList
from nuclino.models.user import User, UserProps
from nuclino.models.workspace import Workspace, WorkspaceProps
from tests.helpers import (
    collection_payload,
    file_payload,
    item_payload,
    user_payload,
    workspace_payload,
)


class DummyNuclino:
    def get_item(self, item_id: str) -> Any:
        return item_id

    def get_file(self, file_id: str) -> Any:
        return file_id

    def get_team(self, team_id: str) -> Any:
        return team_id

    def get_workspace(self, workspace_id: str) -> Any:
        return workspace_id

    def get_workspaces(
        self,
        team_id: str | None = None,
        limit: int | None = None,
        after: str | None = None,
    ) -> Any:
        return [team_id, limit, after]

    def create_item(self, **kwargs: Any) -> Any:
        return kwargs

    def update_item(
        self,
        item_id: str,
        title: str | None = None,
        content: str | None = None,
    ) -> Any:
        return {"id": item_id, "title": title, "content": content}

    def delete_item(self, item_id: str) -> Any:
        return {"id": item_id}


def test_snake_case_attribute_access_matches_public_annotations() -> None:
    dummy = DummyNuclino()

    user = User(cast(UserProps, user_payload()), dummy)
    workspace = Workspace(cast(WorkspaceProps, workspace_payload()), dummy)
    item = Item(cast(ItemProps, item_payload()), dummy)
    collection = Collection(cast(CollectionProps, collection_payload()), dummy)
    file = File(cast(FileProps, file_payload()), dummy)

    assert user.first_name == "Ada"
    assert workspace.team_id == "team-1"
    assert item.workspace_id == "workspace-1"
    assert collection.content_meta["itemIds"] == ["item-2"]
    assert file.item_id == "item-1"


def test_optional_attributes_return_none_without_mutating_payload() -> None:
    dummy = DummyNuclino()
    listed_item = Item(
        cast(ItemProps, {key: value for key, value in item_payload().items() if key != "content"}),
        dummy,
    )
    user = User(
        cast(
            UserProps,
            {
                "object": "user",
                "id": "user-1",
                "firstName": "Ada",
                "lastName": "Lovelace",
                "email": "ada@example.com",
            },
        ),
        dummy,
    )

    assert listed_item.content is None
    assert listed_item.highlight is None
    assert "content" not in listed_item.to_dict()
    assert user.avatar_url is None


def test_to_dict_returns_deep_copy_for_nested_data() -> None:
    item = Item(cast(ItemProps, item_payload()), DummyNuclino())

    copied = item.to_dict()
    copied["contentMeta"]["itemIds"].append("item-99")

    assert item.contentMeta["itemIds"] == []


def test_parse_returns_nuclino_list_with_metadata() -> None:
    client = Client("token")

    parsed = client.parse(
        {
            "object": "list",
            "results": [workspace_payload()],
            "nextCursor": "cursor-1",
        }
    )

    client.close()

    assert isinstance(parsed, NuclinoList)
    assert isinstance(parsed[0], Workspace)
    assert parsed.metadata == {"nextCursor": "cursor-1"}
    assert parsed.to_dict()["object"] == "list"


def test_parse_tolerates_unknown_object_types() -> None:
    client = Client("token")

    parsed = client.parse({"object": "mystery", "id": "m-1"})

    client.close()

    assert parsed == {"object": "mystery", "id": "m-1"}


def test_collection_and_workspace_helpers_accept_collection_content() -> None:
    dummy = DummyNuclino()
    collection = Collection(cast(CollectionProps, collection_payload()), dummy)
    workspace = Workspace(cast(WorkspaceProps, workspace_payload()), dummy)

    created_from_collection = collection.create_collection(title="Nested", content="Body\n")
    updated_collection = collection.update(content="Updated\n")
    created_from_workspace = workspace.create_collection(title="Nested", content="Body\n")

    assert created_from_collection["content"] == "Body\n"
    assert updated_collection["content"] == "Updated\n"
    assert created_from_workspace["content"] == "Body\n"
