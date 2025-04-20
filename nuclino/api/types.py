from typing import Any, Dict, List, TypedDict, TypeVar, Union

from nuclino.models.shared import NuclinoObject


class BaseDeleteResponse(TypedDict):
    """Response type for delete operations"""
    id: str

class ContentMeta(TypedDict):
    """Content metadata type"""
    itemIds: List[str]
    fileIds: List[str]

class DownloadInfo(TypedDict):
    """Download information type"""
    url: str
    expiresAt: str

class ApiResponse(TypedDict):
    """Generic API response type"""
    data: Union[Dict[str, Any], List[Dict[str, Any]]]

# Type variable for generic response handling
T = TypeVar('T', bound=NuclinoObject)
ResponseType = Union[List[T], T, BaseDeleteResponse] 