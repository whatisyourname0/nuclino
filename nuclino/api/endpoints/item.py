from typing import List, Optional, Union

from nuclino.api.client import Client
from nuclino.api.exceptions import NuclinoValidationError
from nuclino.api.types import BaseDeleteResponse
from nuclino.models.item import Collection, Item


class ItemEndpoints:
    """Item and Collection-related API endpoints"""
    
    def __init__(self, client: Client):
        self.client = client

    def get_items(
        self,
        team_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: Optional[int] = None,
        after: Optional[str] = None,
    ) -> List[Union[Item, Collection]]:
        '''
        Get list of items and collection from the team or the workspace.

        :param team_id: ID of the team the returned items should belong to.
        :param workspace_id: ID of the workspace the returned items should belong to.
        :param limit: number between 1 and 100 to limit the results.
        :param after: only return items that come after the given item ID.
        :returns: list of Item and Collection objects.
        '''
        path = '/items'
        params = {}

        if team_id is None and workspace_id is None:
            raise NuclinoValidationError(status_code=400, message="Must specify either team_id or workspace_id")

        if team_id is not None and workspace_id is not None:
            raise NuclinoValidationError(status_code=400, message="Cannot specify both team_id and workspace_id")

        if team_id is not None:
            params['teamId'] = team_id
        if workspace_id is not None:
            params['workspaceId'] = workspace_id
        if limit is not None:
            params['limit'] = str(limit)
        if after is not None:
            params['after'] = after
        return self.client.get(path, params)

    def get_item(self, item_id: str) -> Union[Item, Collection]:
        '''
        Get specific item or collection by ID.

        :param item_id: ID of the item to get.
        :returns: Item or Collection object.
        '''
        path = f'/items/{item_id}'
        return self.client.get(path)

    def create_item(
        self,
        workspace_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        object: str = 'item',
        title: Optional[str] = None,
        content: Optional[str] = None,
        index: Optional[int] = None
    ) -> Union[Item, Collection]:
        '''
        Create a new item or collection.

        :param workspace_id: ID of the workspace the item should be put in.
        :param parent_id: ID of the collection the item should be put in.
        :param object: 'item' or 'collection'.
        :param title: item or collection title.
        :param content: item content (only for items).
        :param index: where to put this item in the tree.
        :returns: the created Item or Collection object.
        '''
        path = '/items'
        data = {'object': object}
        if workspace_id is not None:
            data['workspaceId'] = workspace_id
        if parent_id is not None:
            data['parentId'] = parent_id
        if title is not None:
            data['title'] = title
        if content is not None:
            data['content'] = content
        if index is not None:
            data['index'] = str(index)
        return self.client.post(path, data)

    def update_item(
        self,
        item_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> Union[Item, Collection]:
        '''
        Update item or collection.

        :param item_id: ID of the item to update.
        :param title: new item title.
        :param content: new item content (only for items).
        :returns: updated Item or Collection object.
        '''
        path = f'/items/{item_id}'
        data = {}
        if title is not None:
            data['title'] = title
        if content is not None:
            data['content'] = content
        return self.client.put(path, data=data)

    def delete_item(self, item_id: str) -> BaseDeleteResponse:
        '''
        Move item or collection to trash.

        :param item_id: ID of the item to delete.
        :returns: a dictionary with ID of deleted item.
        '''
        path = f'/items/{item_id}'
        return self.client.delete(path)

    # Convenience methods for collections
    def get_collection(self, collection_id: str) -> Collection:
        '''
        Get specific collection by ID.

        :param collection_id: ID of the collection to get.
        :returns: Collection object.
        '''
        return self.get_item(collection_id)

    def create_collection(
        self,
        workspace_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        title: Optional[str] = None,
        index: Optional[int] = None
    ) -> Collection:
        '''
        Create a collection.

        :param workspace_id: ID of the workspace the collection should be put in.
        :param parent_id: ID of the collection this collection should be put in.
        :param title: collection title.
        :param index: where to put this collection in the tree.
        :returns: the created Collection object.
        '''
        return self.create_item(
            workspace_id=workspace_id,
            parent_id=parent_id,
            object='collection',
            title=title,
            content=None,
            index=index
        )

    def update_collection(
        self,
        collection_id: str,
        title: Optional[str] = None
    ) -> Collection:
        '''
        Update collection.

        :param collection_id: ID of the collection to update.
        :param title: new collection title.
        :returns: updated Collection object.
        '''
        return self.update_item(collection_id, title=title, content=None)

    def delete_collection(self, collection_id: str) -> BaseDeleteResponse:
        '''
        Move collection to trash.

        :param collection_id: ID of the collection to delete.
        :returns: a dictionary with ID of deleted collection.
        '''
        return self.delete_item(collection_id) 