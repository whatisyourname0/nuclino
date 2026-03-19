from typing import cast

from nuclino.api.client import Client
from nuclino.models.user import User


class UserEndpoints:
    """User-related API endpoints."""

    def __init__(self, client: Client) -> None:
        self.client = client

    def get_user(self, user_id: str) -> User:
        return cast(User, self.client.get(f"/users/{user_id}"))
