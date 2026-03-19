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


T = TypeVar("T", bound=NuclinoObject)
ResponseType = Union[NuclinoList[T], T, BaseDeleteResponse, dict[str, Any]]

__all__ = [
    "ApiResponse",
    "BaseDeleteResponse",
    "ContentMeta",
    "DownloadInfo",
    "ResponseType",
]
