from typing import Optional, TypedDict

from .shared import NuclinoObject


class UserProps(TypedDict):
    """User properties as per API specification"""
    id: str
    firstName: str
    lastName: str
    email: str
    avatarUrl: Optional[str]

class User(NuclinoObject):
    """User object as per API specification"""
    _object = "user"
    id: str
    first_name: str
    last_name: str
    email: str
    avatar_url: Optional[str]

    def __init__(self, props: UserProps, nuclino):
        super().__init__(props, nuclino)

    def __repr__(self) -> str:
        return f'<User "{self["firstName"]} {self["lastName"]}">' 