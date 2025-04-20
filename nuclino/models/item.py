from typing import TYPE_CHECKING, Dict, List, Optional, TypedDict, Union

from .shared import NuclinoObject

if TYPE_CHECKING:
    from .file import File
    from .workspace import Workspace

class ItemFields(TypedDict, total=False):
    """Custom fields for items that can have any string key"""
    pass

class ContentMeta(TypedDict):
    """Content metadata for items"""
    itemIds: List[str]
    fileIds: List[str]

class ItemProps(TypedDict):
    """Item properties as per API specification"""
    object: str
    id: str
    workspaceId: str
    url: str
    title: str
    createdAt: str
    createdUserId: str
    lastUpdatedAt: str
    lastUpdatedUserId: str
    fields: ItemFields
    content: Optional[str]
    contentMeta: ContentMeta
    highlight: Optional[str]

class CollectionProps(TypedDict):
    """Collection properties as per API specification"""
    object: str
    id: str
    workspaceId: str
    url: str
    title: str
    createdAt: str
    createdUserId: str
    lastUpdatedAt: str
    lastUpdatedUserId: str
    childIds: List[str]

class Item(NuclinoObject):
    """Item object as per API specification"""
    _object = "item"
    id: str
    workspace_id: str
    url: str
    title: str
    created_at: str
    created_user_id: str
    last_updated_at: str
    last_updated_user_id: str
    fields: ItemFields
    content: Optional[str]
    content_meta: ContentMeta
    highlight: Optional[str]

    def __init__(
        self,
        props: ItemProps,
        nuclino
    ):
        super().__init__(props, nuclino)

    def get_workspace(self) -> 'Workspace':
        '''
        Make an API call to get the workspace this item belongs to.

        :returns: Workspace object.
        '''
        return self._nuclino.get_workspace(self["workspaceId"])

    def get_items(self) -> List[Union['Item', 'Collection']]:
        '''
        Make API calls to get list of items or collections that are referenced in
        this item.

        :returns: list of Item or Collection objects.
        '''
        return [self._nuclino.get_item(id_) for id_ in self["contentMeta"]["itemIds"]]

    def get_files(self) -> List['File']:
        '''
        Make API calls to get the list of files attached to this file.

        :returns: list of File objects.
        '''
        return [self._nuclino.get_file(id_) for id_ in self["contentMeta"]["fileIds"]]

    def delete(self) -> Dict[str, str]:
        '''
        Move this item to trash.

        :returns: dictionary with this item id.
        '''
        return self._nuclino.delete_item(self["id"])

    def update(
        self,
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> 'Item':
        '''
        Update this item.

        :param title: new item title.
        :param content: new item content.

        :returns: updated Item object.
        '''
        return self._nuclino.update_item(self["id"], title, content)

    def __repr__(self):
        return f'<Item "{self["title"]}">'


class Collection(NuclinoObject):
    """Collection object as per API specification"""
    _object = "collection"
    id: str
    workspace_id: str
    url: str
    title: str
    created_at: str
    created_user_id: str
    last_updated_at: str
    last_updated_user_id: str
    child_ids: List[str]

    def __init__(
        self,
        props: CollectionProps,
        nuclino
    ):
        super().__init__(props, nuclino)

    def get_children(self) -> List[Union[Item, 'Collection']]:
        '''
        Make an API call to get the list of direct children of this collection.

        :returns: list of Item and Collection objects.
        '''
        return [self._nuclino.get_item(id_) for id_ in self["childIds"]]

    def get_workspace(self) -> 'Workspace':
        '''
        Make an API call to get the workspace this collection belongs to.

        :returns: Workspace object.
        '''
        return self._nuclino.get_workspace(self["workspaceId"])

    def create_item(
        self,
        object: str = 'item',
        title: Optional[str] = None,
        content: Optional[str] = None,
        index: Optional[int] = None
    ) -> Union[Item, 'Collection']:
        '''
        Create an item or a collection under this collection.

        :param object: 'item' or 'collection'.
        :param title: item title.
        :param content: item content.
        :param index: where to put this item in the tree.

        :returns: created Item or Collection object.
        '''
        return self._nuclino.create_item(
            parent_id=self["id"],
            object=object,
            title=title,
            content=content,
            index=index
        )

    def create_collection(
        self,
        title: Optional[str] = None,
        index: Optional[int] = None
    ) -> 'Collection':
        '''
        Create another collection under this collection.

        :param title: collection title.
        :param index: where to put this collection in the tree.

        :returns: created Collection object.
        '''
        return self._nuclino.create_item(
            parent_id=self["id"],
            object="collection",
            title=title,
            index=index
        )

    def delete(self) -> Dict[str, str]:
        '''
        Move this collection to trash.

        :returns: dictionary with this collection ID.
        '''
        return self._nuclino.delete_collection(self["id"])

    def update(
        self,
        title: Optional[str] = None
    ) -> 'Collection':
        '''
        Change this collection title.

        :param title: new title value.

        :returns: updated Collection object.
        '''
        return self._nuclino.update_collection(self["id"], title)

    def __repr__(self) -> str:
        return f'<Collection "{self["title"]}">'
