from typing import cast

from nuclino.api.client import Client
from nuclino.models.file import File


class FileEndpoints:
    """File-related API endpoints."""

    def __init__(self, client: Client) -> None:
        self.client = client

    def get_file(self, file_id: str) -> File:
        return cast(File, self.client.get(f"/files/{file_id}"))
