from __future__ import annotations

from typing import Any, cast
from unittest.mock import Mock

import pytest

from nuclino.api.client import Client
from nuclino.api.endpoints.item import ItemEndpoints
from nuclino.api.endpoints.team import TeamEndpoints
from nuclino.api.endpoints.workspace import WorkspaceEndpoints
from nuclino.api.exceptions import NuclinoClientValidationError
from nuclino.models.item import Collection, CollectionProps
from nuclino.models.shared import NuclinoList
from nuclino.models.team import Team, TeamProps
from nuclino.models.workspace import Workspace, WorkspaceProps
from tests.helpers import collection_payload, item_payload


def test_create_item_requires_exactly_one_scope() -> None:
    endpoints = ItemEndpoints(Mock(spec=Client))

    with pytest.raises(NuclinoClientValidationError):
        endpoints.create_item()

    with pytest.raises(NuclinoClientValidationError):
        endpoints.create_item(workspace_id="workspace-1", parent_id="collection-1")


def test_create_item_validates_object_name() -> None:
    endpoints = ItemEndpoints(Mock(spec=Client))

    with pytest.raises(NuclinoClientValidationError):
        endpoints.create_item(workspace_id="workspace-1", object="database")


def test_create_item_preserves_integer_index() -> None:
    client = Mock(spec=Client)
    client.post.return_value = item_payload()
    endpoints = ItemEndpoints(client)

    endpoints.create_item(workspace_id="workspace-1", index=2)

    assert client.post.call_args.args[1]["index"] == 2


def test_collection_helpers_return_collection_types() -> None:
    client = Mock(spec=Client)
    client.post.return_value = Collection(cast(CollectionProps, collection_payload()), cast(Any, client))
    client.get.return_value = Collection(cast(CollectionProps, collection_payload()), cast(Any, client))
    endpoints = ItemEndpoints(client)

    created = endpoints.create_collection(workspace_id="workspace-1")
    fetched = endpoints.get_collection("collection-1")

    assert created.object == "collection"
    assert fetched.object == "collection"


def test_create_collection_forwards_content() -> None:
    client = Mock(spec=Client)
    client.post.return_value = Collection(cast(CollectionProps, collection_payload()), cast(Any, client))
    endpoints = ItemEndpoints(client)

    endpoints.create_collection(workspace_id="workspace-1", content="Nested\n")

    assert client.post.call_args.args == (
        "/items",
        {"object": "collection", "workspaceId": "workspace-1", "content": "Nested\n"},
    )


def test_update_collection_forwards_content() -> None:
    client = Mock(spec=Client)
    client.put.return_value = Collection(cast(CollectionProps, collection_payload()), cast(Any, client))
    endpoints = ItemEndpoints(client)

    endpoints.update_collection("collection-1", content="Updated\n")

    assert client.put.call_args.args == (
        "/items/collection-1",
        {"content": "Updated\n"},
    )


def test_get_items_includes_search_query() -> None:
    client = Mock(spec=Client)
    client.get.return_value = NuclinoList([])
    endpoints = ItemEndpoints(client)

    endpoints.get_items(workspace_id="workspace-1", search="hello")

    assert client.get.call_args.args == (
        "/items",
        {"workspaceId": "workspace-1", "search": "hello"},
    )


@pytest.mark.parametrize("limit", [0, 101])
def test_endpoints_validate_limit_range(limit: int) -> None:
    item_endpoints = ItemEndpoints(Mock(spec=Client))
    team_endpoints = TeamEndpoints(Mock(spec=Client))
    workspace_endpoints = WorkspaceEndpoints(Mock(spec=Client))

    with pytest.raises(NuclinoClientValidationError):
        item_endpoints.get_items(workspace_id="workspace-1", limit=limit)

    with pytest.raises(NuclinoClientValidationError):
        team_endpoints.get_teams(limit=limit)

    with pytest.raises(NuclinoClientValidationError):
        workspace_endpoints.get_workspaces(limit=limit)


def test_iter_teams_follows_next_cursor() -> None:
    client = Mock(spec=Client)
    client.get.side_effect = [
        NuclinoList(
            [Team(cast(TeamProps, {"object": "team", "id": "team-1", "url": "u1", "name": "A", "createdAt": "t", "createdUserId": "u"}), cast(Any, client))],
            metadata={"nextCursor": "cursor-1"},
        ),
        NuclinoList(
            [Team(cast(TeamProps, {"object": "team", "id": "team-2", "url": "u2", "name": "B", "createdAt": "t", "createdUserId": "u"}), cast(Any, client))],
        ),
    ]
    endpoints = TeamEndpoints(client)

    teams = list(endpoints.iter_teams(limit=50))

    assert [team.id for team in teams] == ["team-1", "team-2"]
    assert client.get.call_args_list[0].args == ("/teams", {"limit": 50})
    assert client.get.call_args_list[1].args == ("/teams", {"limit": 50, "after": "cursor-1"})


def test_iter_teams_falls_back_to_last_item_id() -> None:
    client = Mock(spec=Client)
    client.get.side_effect = [
        NuclinoList(
            [Team(cast(TeamProps, {"object": "team", "id": "team-1", "url": "u1", "name": "A", "createdAt": "t", "createdUserId": "u"}), cast(Any, client))],
        ),
        NuclinoList([]),
    ]
    endpoints = TeamEndpoints(client)

    teams = list(endpoints.iter_teams(limit=1))

    assert [team.id for team in teams] == ["team-1"]
    assert client.get.call_args_list[1].args == ("/teams", {"limit": 1, "after": "team-1"})


def test_iter_workspaces_follows_next_cursor() -> None:
    client = Mock(spec=Client)
    client.get.side_effect = [
        NuclinoList(
            [Workspace(cast(WorkspaceProps, {"object": "workspace", "id": "workspace-1", "teamId": "team-1", "name": "Docs", "createdAt": "t", "createdUserId": "u", "childIds": [], "fields": []}), cast(Any, client))],
            metadata={"nextCursor": "cursor-1"},
        ),
        NuclinoList(
            [Workspace(cast(WorkspaceProps, {"object": "workspace", "id": "workspace-2", "teamId": "team-1", "name": "Ops", "createdAt": "t", "createdUserId": "u", "childIds": [], "fields": []}), cast(Any, client))],
        ),
    ]
    endpoints = WorkspaceEndpoints(client)

    workspaces = list(endpoints.iter_workspaces(team_id="team-1"))

    assert [workspace.id for workspace in workspaces] == ["workspace-1", "workspace-2"]
    assert client.get.call_args_list[0].args == ("/workspaces", {"teamId": "team-1", "limit": 100})
    assert client.get.call_args_list[1].args == (
        "/workspaces",
        {"teamId": "team-1", "limit": 100, "after": "cursor-1"},
    )


def test_iter_items_follows_next_cursor() -> None:
    client = Mock(spec=Client)
    client.get.side_effect = [
        NuclinoList([Collection(cast(CollectionProps, collection_payload()), cast(Any, client))], metadata={"nextCursor": "cursor-1"}),
        NuclinoList([Collection(cast(CollectionProps, collection_payload() | {"id": "collection-2"}), cast(Any, client))]),
    ]
    endpoints = ItemEndpoints(client)

    items = list(endpoints.iter_items(workspace_id="workspace-1", limit=25))

    assert [item.id for item in items] == ["collection-1", "collection-2"]
    assert client.get.call_args_list[0].args == ("/items", {"workspaceId": "workspace-1", "limit": 25})
    assert client.get.call_args_list[1].args == (
        "/items",
        {"workspaceId": "workspace-1", "limit": 25, "after": "cursor-1"},
    )


def test_iter_items_preserves_search_query() -> None:
    client = Mock(spec=Client)
    client.get.side_effect = [
        NuclinoList(
            [Collection(cast(CollectionProps, collection_payload()), cast(Any, client))],
            metadata={"nextCursor": "cursor-1"},
        ),
        NuclinoList(
            [Collection(cast(CollectionProps, collection_payload() | {"id": "collection-2"}), cast(Any, client))],
        ),
    ]
    endpoints = ItemEndpoints(client)

    list(endpoints.iter_items(workspace_id="workspace-1", search="hello", limit=25))

    assert client.get.call_args_list[0].args == (
        "/items",
        {"workspaceId": "workspace-1", "search": "hello", "limit": 25},
    )
    assert client.get.call_args_list[1].args == (
        "/items",
        {"workspaceId": "workspace-1", "search": "hello", "limit": 25, "after": "cursor-1"},
    )


def test_iter_items_falls_back_to_last_item_id() -> None:
    client = Mock(spec=Client)
    client.get.side_effect = [
        NuclinoList(
            [Collection(cast(CollectionProps, collection_payload()), cast(Any, client))],
        ),
        NuclinoList([]),
    ]
    endpoints = ItemEndpoints(client)

    items = list(endpoints.iter_items(workspace_id="workspace-1", limit=1))

    assert [item.id for item in items] == ["collection-1"]
    assert client.get.call_args_list[1].args == (
        "/items",
        {"workspaceId": "workspace-1", "limit": 1, "after": "collection-1"},
    )
