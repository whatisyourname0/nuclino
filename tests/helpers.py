from __future__ import annotations

from typing import Any


class DummyResponse:
    def __init__(
        self,
        status_code: int,
        json_data: Any = None,
        *,
        text: str = "",
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self._json_data = json_data
        self.text = text
        self.headers = headers or {}
        self.content = text.encode() if text else (b"" if json_data is None else b"json")
        self.reason = text or ""

    def json(self) -> Any:
        if isinstance(self._json_data, BaseException):
            raise self._json_data
        return self._json_data


def user_payload() -> dict[str, Any]:
    return {
        "object": "user",
        "id": "user-1",
        "firstName": "Ada",
        "lastName": "Lovelace",
        "email": "ada@example.com",
        "avatarUrl": None,
    }


def workspace_payload() -> dict[str, Any]:
    return {
        "object": "workspace",
        "id": "workspace-1",
        "teamId": "team-1",
        "name": "General",
        "createdAt": "2024-01-01T00:00:00Z",
        "createdUserId": "user-1",
        "childIds": [],
        "fields": [],
    }


def item_payload() -> dict[str, Any]:
    return {
        "object": "item",
        "id": "item-1",
        "workspaceId": "workspace-1",
        "url": "https://app.nuclino.com/item-1",
        "title": "Title",
        "createdAt": "2024-01-01T00:00:00Z",
        "createdUserId": "user-1",
        "lastUpdatedAt": "2024-01-01T00:00:00Z",
        "lastUpdatedUserId": "user-1",
        "fields": {"Priority": "High"},
        "content": "Hello\n",
        "contentMeta": {"itemIds": [], "fileIds": []},
    }


def collection_payload() -> dict[str, Any]:
    return {
        "object": "collection",
        "id": "collection-1",
        "workspaceId": "workspace-1",
        "url": "https://app.nuclino.com/collection-1",
        "title": "Collection",
        "createdAt": "2024-01-01T00:00:00Z",
        "createdUserId": "user-1",
        "lastUpdatedAt": "2024-01-01T00:00:00Z",
        "lastUpdatedUserId": "user-1",
        "childIds": [],
        "content": "Nested\n",
        "contentMeta": {"itemIds": ["item-2"], "fileIds": ["file-1"]},
    }


def team_payload() -> dict[str, Any]:
    return {
        "object": "team",
        "id": "team-1",
        "url": "https://app.nuclino.com/team-1",
        "name": "Team",
        "createdAt": "2024-01-01T00:00:00Z",
        "createdUserId": "user-1",
    }


def file_payload() -> dict[str, Any]:
    return {
        "object": "file",
        "id": "file-1",
        "itemId": "item-1",
        "fileName": "diagram.png",
        "createdAt": "2024-01-01T00:00:00Z",
        "createdUserId": "user-1",
        "download": {
            "url": "https://download.example.com/file-1",
            "expiresAt": "2024-01-01T01:00:00Z",
        },
    }
