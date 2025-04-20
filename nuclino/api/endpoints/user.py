from nuclino.api.client import Client
from nuclino.models.user import User


class UserEndpoints:
    """User-related API endpoints"""
    
    def __init__(self, client: Client):
        self.client = client

    def get_user(self, user_id: str) -> User:
        '''
        Get information associated with a specific user by ID.

        :param user_id: ID of the user to get.
        :returns: a User object
        '''
        path = f'/users/{user_id}'
        return self.client.get(path) 