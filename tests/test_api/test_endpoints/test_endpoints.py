from __future__ import annotations

from typing import Any, cast
from unittest.mock import Mock

import pytest

from nuclino.api.client import Client
from nuclino.api.endpoints.item import ItemEndpoints
from nuclino.api.endpoints.team import TeamEndpoints
from nuclino.api.endpoints.workspace import WorkspaceEndpoints
from nuclino.api.exceptions import NuclinoValidationError
from nuclino.models.item import Collection, CollectionProps
from tests.helpers import collection_payload, item_payload


def test_create_item_requires_exactly_one_scope() -> None:
    endpoints = ItemEndpoints(Mock(spec=Client))

    with pytest.raises(NuclinoValidationError):
        endpoints.create_item()

    with pytest.raises(NuclinoValidationError):
        endpoints.create_item(workspace_id="workspace-1", parent_id="collection-1")


def test_create_item_validates_object_name() -> None:
    endpoints = ItemEndpoints(Mock(spec=Client))

    with pytest.raises(NuclinoValidationError):
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


@pytest.mark.parametrize("limit", [0, 101])
def test_endpoints_validate_limit_range(limit: int) -> None:
    item_endpoints = ItemEndpoints(Mock(spec=Client))
    team_endpoints = TeamEndpoints(Mock(spec=Client))
    workspace_endpoints = WorkspaceEndpoints(Mock(spec=Client))

    with pytest.raises(NuclinoValidationError):
        item_endpoints.get_items(workspace_id="workspace-1", limit=limit)

    with pytest.raises(NuclinoValidationError):
        team_endpoints.get_teams(limit=limit)

    with pytest.raises(NuclinoValidationError):
        workspace_endpoints.get_workspaces(limit=limit)
