from typing import Any, Mapping, TypedDict, TypeVar, Union

from nuclino.models.file import DownloadInfo
from nuclino.models.item import ContentMeta
from nuclino.models.shared import NuclinoList, NuclinoObject


class BaseDeleteResponse(TypedDict):
    """Response type for delete operations."""

    id: str


class ApiResponse(TypedDict):
    """Generic API response type."""

    data: Mapping[str, Any]


class ItemListParams(TypedDict, total=False):
    """Query parameters for listing or searching items."""

    teamId: str
    workspaceId: str
    search: str
    limit: int
    after: str


class ItemCreatePayload(TypedDict, total=False):
    """Request body for creating an item or collection."""

    object: str
    workspaceId: str
    parentId: str
    title: str
    content: str
    index: int


class ItemUpdatePayload(TypedDict, total=False):
    """Request body for updating an item or collection."""

    title: str
    content: str


T = TypeVar("T", bound=NuclinoObject)
ResponseType = Union[NuclinoList[T], T, BaseDeleteResponse, dict[str, Any]]

__all__ = [
    "ApiResponse",
    "BaseDeleteResponse",
    "ContentMeta",
    "DownloadInfo",
    "ItemCreatePayload",
    "ItemListParams",
    "ItemUpdatePayload",
    "ResponseType",
]
