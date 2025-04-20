from typing import List, Optional

from nuclino.api.client import Client
from nuclino.models.workspace import Workspace


class WorkspaceEndpoints:
    """Workspace-related API endpoints"""
    
    def __init__(self, client: Client):
        self.client = client

    def get_workspaces(
        self,
        team_id: Optional[str] = None,
        limit: Optional[int] = None,
        after: Optional[str] = None
    ) -> List[Workspace]:
        '''
        Get list of workspaces available for user.

        :param team_id: ID of the team the returned workspaces should belong to.
        :param limit: number between 1 and 100 to limit the results.
        :param after: only return workspaces that come after the given workspace ID.
        :returns: list of Workspace objects.
        '''
        path = '/workspaces'
        params = {}
        if team_id is not None:
            params['teamId'] = team_id
        if limit is not None:
            params['limit'] = str(limit)
        if after is not None:
            params['after'] = after
        return self.client.get(path, params)

    def get_workspace(self, workspace_id: str) -> Workspace:
        '''
        Get specific workspace by ID.

        :param workspace_id: ID of the workspace to get.
        :returns: Workspace object.
        '''
        path = f'/workspaces/{workspace_id}'
        return self.client.get(path) 