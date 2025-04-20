from typing import TYPE_CHECKING, TypedDict

from .shared import NuclinoObject

if TYPE_CHECKING:
    from .item import Item

class DownloadInfo(TypedDict):
    """Download information for files"""
    url: str
    expiresAt: str

class FileProps(TypedDict):
    """File properties as per API specification"""
    object: str
    id: str
    itemId: str
    fileName: str
    createdAt: str
    createdUserId: str
    download: DownloadInfo

class File(NuclinoObject):
    """File object as per API specification"""
    _object = "file"
    object: str
    id: str
    item_id: str
    file_name: str
    created_at: str
    created_user_id: str
    download: DownloadInfo

    def __init__(
        self,
        props: FileProps,
        nuclino
    ):
        super().__init__(props, nuclino)

    def get_item(self) -> 'Item':
        '''
        Make an API call to get the item this file is attached to.

        :returns: Item object.
        '''
        return self._nuclino.get_item(self["itemId"])

    def __repr__(self):
        return f'<file "{self["fileName"]}">'
