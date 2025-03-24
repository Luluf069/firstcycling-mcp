"""
API
=========

Provides tools to access the FirstCycling API.
"""

from slumber import API
from bs4 import BeautifulSoup
import re

class FirstCyclingAPI(API):
    """ Wrapper for FirstCycling API """
    def __init__(self):
        super().__init__("https://firstcycling.com", append_slash=False)
        
    def __getitem__(self, key):
        return getattr(self, key)
    
    def _fix_kwargs(self, **kwargs):
        return {k: v for k, v in kwargs.items() if v}
    
    def _get_resource_response(self, resource, **kwargs):
        return self._store['session'].get(resource.url(), params=self._fix_kwargs(**kwargs)).content

    def get_rider_endpoint(self, rider_id, **kwargs):
        return self._get_resource_response(self['rider.php'], r=rider_id, **kwargs)

    def get_race_endpoint(self, race_id, **kwargs):
        return self._get_resource_response(self['race.php'], r=race_id, **kwargs)

    def get_ranking_endpoint(self, **kwargs):
        return self._get_resource_response(self['ranking.php'], **kwargs)

    def search(self, query):
        """
        Search for riders and races by name.

        Parameters
        ----------
        query : str
            The search query string

        Returns
        -------
        dict
            Dictionary containing lists of matching riders and races with their IDs
            {
                'riders': [
                    {'id': int, 'name': str, 'nationality': str, 'team': str},
                    ...
                ],
                'races': [
                    {'id': int, 'name': str, 'country': str},
                    ...
                ]
            }
        """
        response = self._get_resource_response(self['search.php'], s=query)
        soup = BeautifulSoup(response, 'html.parser')
        
        results = {
            'riders': [],
            'races': []
        }
        
        # Parse riders
        rider_tables = soup.find_all('table', class_='sortRiders')
        for table in rider_tables:
            for row in table.find_all('tr', class_=['men', 'women']):
                rider_link = row.find('a')
                if not rider_link:
                    continue
                    
                rider_id = int(re.search(r'r=(\d+)', rider_link['href']).group(1))
                rider_name = rider_link.get_text().strip()
                
                # Get nationality from flag class
                flag_span = row.find('span', class_='flag')
                nationality = flag_span['class'][1].replace('flag-', '') if flag_span else None
                
                # Get team if available
                team_span = row.find('span', style='color:grey')
                team = team_span.get_text().strip() if team_span else None
                
                results['riders'].append({
                    'id': rider_id,
                    'name': rider_name,
                    'nationality': nationality,
                    'team': team
                })
        
        # Parse races
        race_table = soup.find('table', class_='tablesorter')
        if race_table:
            for row in race_table.find_all('tr', class_=['men', 'women']):
                race_link = row.find('a')
                if not race_link:
                    continue
                    
                race_id = int(re.search(r'r=(\d+)', race_link['href']).group(1))
                race_name = race_link.get_text().strip()
                
                # Get country from flag class
                flag_span = row.find('span', class_='flag')
                country = flag_span['class'][1].replace('flag-', '') if flag_span else None
                
                results['races'].append({
                    'id': race_id,
                    'name': race_name,
                    'country': country
                })
        
        return results

fc = FirstCyclingAPI()