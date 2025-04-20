from typing import TYPE_CHECKING, List, TypedDict

from .shared import NuclinoObject

if TYPE_CHECKING:
    from .workspace import Workspace

class TeamProps(TypedDict):
    """Team properties as per API specification"""
    object: str
    id: str
    url: str
    name: str
    createdAt: str
    createdUserId: str

class Team(NuclinoObject):
    """Team object as per API specification"""
    _object = "team"
    object: str
    id: str
    url: str
    name: str
    created_at: str
    created_user_id: str

    def __init__(
        self,
        props: TeamProps,
        nuclino
    ):
        super().__init__(props, nuclino)

    def get_workspaces(self) -> List['Workspace']:
        '''
        Make an API call to get all workspaces that belong to this team.

        :returns: list of Workspace objects.
        '''
        return self._nuclino.get_workspaces(team_id=self["id"])

    def __repr__(self) -> str:
        return f'<Team "{self["name"]}">'