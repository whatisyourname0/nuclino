from typing import Literal, NotRequired, Optional, TypedDict

from .shared import NuclinoClient, NuclinoObject


class UserProps(TypedDict):
    """User properties as per API specification"""
    object: NotRequired[Literal["user"]]
    id: str
    firstName: str
    lastName: str
    email: str
    avatarUrl: NotRequired[Optional[str]]

class User(NuclinoObject):
    """User object as per API specification"""
    _object = "user"
    _optional_fields = frozenset({"avatarUrl"})
    id: str
    first_name: str
    last_name: str
    email: str
    avatar_url: Optional[str]

    def __init__(self, props: UserProps, nuclino: NuclinoClient) -> None:
        super().__init__(props, nuclino)

    def __repr__(self) -> str:
        return f'<User "{self["firstName"]} {self["lastName"]}">' 
