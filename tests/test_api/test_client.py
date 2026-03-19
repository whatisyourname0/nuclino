from __future__ import annotations

from typing import Any, cast

import pytest
import requests

from nuclino.api.client import Client
from nuclino.api.exceptions import NuclinoHTTPException, NuclinoRateLimitError, NuclinoTimeoutError
from nuclino.models.item import Item
from nuclino.models.shared import NuclinoList
from nuclino.models.workspace import Workspace
from tests.helpers import DummyResponse, item_payload, workspace_payload


def test_timeout_errors_are_wrapped() -> None:
    client = Client("token")

    def fake_request(*args: object, **kwargs: object) -> object:
        raise requests.Timeout("slow network")

    cast(Any, client.session).request = fake_request

    with pytest.raises(NuclinoTimeoutError):
        client.get("/workspaces")

    client.close()


def test_request_errors_are_wrapped() -> None:
    client = Client("token")

    def fake_request(*args: object, **kwargs: object) -> object:
        raise requests.ConnectionError("offline")

    cast(Any, client.session).request = fake_request

    with pytest.raises(NuclinoHTTPException):
        client.get("/workspaces")

    client.close()


def test_client_retries_429_responses(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client("token")
    responses = iter(
        [
            DummyResponse(429, {"message": "Too many requests", "retry_after": 0}),
            DummyResponse(200, {"data": workspace_payload()}),
        ]
    )

    def fake_request(*args: object, **kwargs: object) -> DummyResponse:
        return next(responses)

    slept: list[float] = []
    monkeypatch.setattr("nuclino.api.client.sleep", lambda seconds: slept.append(seconds))
    cast(Any, client.session).request = fake_request

    parsed = client.get("/workspaces")

    client.close()

    assert isinstance(parsed, Workspace)
    assert slept == [0.0]


def test_rate_limit_error_exposes_retry_after_from_headers() -> None:
    client = Client("token")
    client.max_rate_limit_retries = 0
    cast(Any, client.session).request = (
        lambda *args, **kwargs: DummyResponse(
            429,
            {"message": "Too many requests"},
            headers={"Retry-After": "3"},
        )
    )

    with pytest.raises(NuclinoRateLimitError) as exc_info:
        client.get("/workspaces")

    client.close()

    assert exc_info.value.retry_after == 3


def test_client_accepts_201_created_responses() -> None:
    client = Client("token")
    cast(Any, client.session).request = (
        lambda *args, **kwargs: DummyResponse(201, {"data": item_payload()})
    )

    parsed = client.post("/items", {"workspaceId": "workspace-1"})

    client.close()

    assert isinstance(parsed, Item)


def test_client_handles_204_no_content() -> None:
    client = Client("token")
    cast(Any, client.session).request = lambda *args, **kwargs: DummyResponse(204)

    parsed = client.delete("/items/item-1")

    client.close()

    assert parsed == {}


def test_list_responses_remain_list_like() -> None:
    client = Client("token")
    cast(Any, client.session).request = (
        lambda *args, **kwargs: DummyResponse(
            200,
            {"data": {"object": "list", "results": [workspace_payload()], "nextCursor": "n-1"}},
        )
    )

    parsed = client.get("/workspaces")

    client.close()

    assert isinstance(parsed, NuclinoList)
    assert parsed.metadata == {"nextCursor": "n-1"}
