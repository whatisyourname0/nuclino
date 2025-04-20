from typing import TYPE_CHECKING, List, Optional, TypedDict, Union

from .field import FieldProps
from .shared import NuclinoObject

if TYPE_CHECKING:
    from .item import Collection, Item
    from .team import Team

class WorkspaceProps(TypedDict):
    """Workspace properties as per API specification"""
    id: str
    teamId: str
    name: str
    createdAt: str
    createdUserId: str
    childIds: List[str]
    fields: List[FieldProps]
    object: str

class Workspace(NuclinoObject):
    """Workspace object as per API specification"""
    _object = "workspace"
    id: str
    team_id: str
    name: str
    created_at: str
    created_user_id: str
    child_ids: List[str]
    fields: List[FieldProps]

    def __init__(
        self,
        props: WorkspaceProps,
        nuclino
    ):
        super().__init__(props, nuclino)

    def get_team(self) -> 'Team':
        '''
        Make an API call to get the team this workspace belongs to.

        :returns: Team object.
        '''
        return self._nuclino.get_team(self["teamId"])

    def get_children(self) -> List[Union['Item', 'Collection']]:
        return [self._nuclino.get_item(id_) for id_ in self["childIds"]]

    def create_item(
        self,
        object: str = 'item',
        title: Optional[str] = None,
        content: Optional[str] = None,
        index: Optional[int] = None
    ) -> Union['Item', 'Collection']:
        '''
        Create a new item or collection under this workspace.

        :param object: 'item' or 'collection'.
        :param title: item title.
        :param content: item content (only for items).
        :param index: where to put this item in the tree.

        :returns: Item or Collection object.
        '''
        return self._nuclino.create_item(
            workspace_id=self["id"],
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
        Create a new collection under this workspace.

        :param title: collection title.
        :param index: where to put this collection in the tree.

        :returns: Collection object.
        '''
        return self._nuclino.create_item(
            workspace_id=self["id"],
            object="collection",
            title=title,
            content=None,
            index=index
        )

    def __repr__(self) -> str:
        return f'<Workspace "{self["name"]}">'