from typing import List, Optional

from nuclino.api.client import Client
from nuclino.models.team import Team


class TeamEndpoints:
    """Team-related API endpoints"""
    
    def __init__(self, client: Client):
        self.client = client

    def get_teams(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None
    ) -> List[Team]:
        '''
        Get list of teams available for user.

        :param limit: number between 1 and 100 to limit the results.
        :param after: only return teams that come after the given team ID.
        :returns: list of Team objects.
        '''
        path = '/teams'
        params = {}
        if limit is not None:
            params['limit'] = str(limit)
        if after is not None:
            params['after'] = after
        return self.client.get(path, params)

    def get_team(self, team_id: str) -> Team:
        '''
        Get specific team by ID.

        :param team_id: ID of the team to get.
        :returns: Team object.
        '''
        path = f'/teams/{team_id}'
        return self.client.get(path) 