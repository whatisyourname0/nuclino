from nuclino.api.client import Client
from nuclino.models.file import File


class FileEndpoints:
    """File-related API endpoints"""
    
    def __init__(self, client: Client):
        self.client = client

    def get_file(self, file_id: str) -> File:
        '''
        Get a file object by ID.

        :param file_id: ID of the file to get.
        :returns: a File object.
        '''
        path = f'/files/{file_id}'
        return self.client.get(path) 