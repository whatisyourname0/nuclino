from __future__ import annotations

from typing import Any, cast

import pytest
import requests

from nuclino.api.client import Client
from nuclino.api.exceptions import (
    NuclinoAuthenticationError,
    NuclinoError,
    NuclinoHTTPException,
    NuclinoNotFoundError,
    NuclinoPermissionError,
    NuclinoRateLimitError,
    NuclinoResponseFormatError,
    NuclinoServerError,
    NuclinoTimeoutError,
    NuclinoTransportError,
    NuclinoValidationError,
)
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

    with pytest.raises(NuclinoTransportError) as exc_info:
        client.get("/workspaces")

    client.close()

    assert exc_info.value.request_data == {"method": "GET", "path": "/workspaces"}


def test_client_retries_429_responses(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Client("token")
    responses = iter(
        [
            DummyResponse(429, {"status": "fail", "message": "Too many requests", "retry_after": 0}),
            DummyResponse(200, {"status": "success", "data": workspace_payload()}),
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
            {"status": "fail", "message": "Too many requests"},
            headers={"Retry-After": "3"},
        )
    )

    with pytest.raises(NuclinoRateLimitError) as exc_info:
        client.get("/workspaces")

    client.close()

    assert exc_info.value.retry_after == 3


def test_rate_limit_error_handles_non_mapping_error_body() -> None:
    client = Client("token")
    client.max_rate_limit_retries = 0
    cast(Any, client.session).request = lambda *args, **kwargs: DummyResponse(429, ["too-many-requests"])

    with pytest.raises(NuclinoRateLimitError) as exc_info:
        client.get("/workspaces")

    client.close()

    assert exc_info.value.message == "Request failed"
    assert exc_info.value.retry_after is None
    assert exc_info.value.response_data["raw_content"] == ""


@pytest.mark.parametrize(
    ("status_code", "exception_type", "message"),
    [
        (400, NuclinoValidationError, "Bad request"),
        (401, NuclinoAuthenticationError, "Unauthorized"),
        (403, NuclinoPermissionError, "Forbidden"),
        (404, NuclinoNotFoundError, "Not found"),
        (500, NuclinoServerError, "Unexpected server error"),
    ],
)
def test_client_maps_error_status_codes_to_specific_exceptions(
    status_code: int,
    exception_type: type[NuclinoHTTPException],
    message: str,
) -> None:
    client = Client("token")
    status = "fail" if 400 <= status_code < 500 else "error"
    cast(Any, client.session).request = (
        lambda *args, **kwargs: DummyResponse(status_code, {"status": status, "message": message})
    )

    with pytest.raises(exception_type) as exc_info:
        client.get("/workspaces")

    client.close()

    assert exc_info.value.status_code == status_code
    assert exc_info.value.message == message
    assert exc_info.value.response_status == status


def test_client_accepts_201_created_responses() -> None:
    client = Client("token")
    cast(Any, client.session).request = (
        lambda *args, **kwargs: DummyResponse(201, {"status": "success", "data": item_payload()})
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
            {
                "status": "success",
                "data": {"object": "list", "results": [workspace_payload()], "nextCursor": "n-1"},
            },
        )
    )

    parsed = client.get("/workspaces")

    client.close()

    assert isinstance(parsed, NuclinoList)
    assert parsed.metadata == {"nextCursor": "n-1"}


def test_client_requires_success_status_in_successful_responses() -> None:
    client = Client("token")
    cast(Any, client.session).request = (
        lambda *args, **kwargs: DummyResponse(200, {"status": "fail", "data": workspace_payload()})
    )

    with pytest.raises(NuclinoResponseFormatError) as exc_info:
        client.get("/workspaces")

    client.close()

    assert exc_info.value.status_code == 200
    assert exc_info.value.response_status == "fail"


def test_client_requires_data_in_successful_responses() -> None:
    client = Client("token")
    cast(Any, client.session).request = (
        lambda *args, **kwargs: DummyResponse(200, {"status": "success"})
    )

    with pytest.raises(NuclinoResponseFormatError) as exc_info:
        client.get("/workspaces")

    client.close()

    assert exc_info.value.message == "Invalid API response: missing data"


def test_client_uses_injected_session_and_sets_auth_header() -> None:
    session = requests.Session()
    client = Client("token", session=session)

    assert client.session is session
    assert session.headers["Authorization"] == "token"

    client.close()


def test_client_does_not_close_injected_session() -> None:
    session = requests.Session()
    closed = False

    def fake_close() -> None:
        nonlocal closed
        closed = True

    cast(Any, session).close = fake_close
    client = Client("token", session=session)

    client.close()

    assert closed is False


def test_all_client_exceptions_are_wrapped_by_nuclino_error_root() -> None:
    assert issubclass(NuclinoHTTPException, NuclinoError)
    assert issubclass(NuclinoTransportError, NuclinoError)
    assert issubclass(NuclinoTimeoutError, NuclinoError)


def test_exception_categories_support_branching() -> None:
    assert NuclinoTransportError("offline").category == "transport"
    assert NuclinoTimeoutError("slow network").category == "timeout"
    assert NuclinoValidationError(400, "Bad request", {"status": "fail"}).category == "http"
    assert NuclinoResponseFormatError(200, "Invalid API response", {"status": "fail"}).category == "response_format"
