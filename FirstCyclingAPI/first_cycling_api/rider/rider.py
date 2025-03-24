from ..objects import FirstCyclingObject
from .endpoints import RiderEndpoint, RiderYearResults
from ..api import fc
import requests
from bs4 import BeautifulSoup
import re
import difflib  # Add import for difflib

def normalize(text):
	"""
	Normalize rider names for better matching.
	
	Parameters:
		text (str): The text to normalize
		
	Returns:
		str: Normalized text
	"""
	# Convert to lowercase and replace dashes with spaces, remove excess whitespace
	text = text.lower()
	text = re.sub(r'[-]', ' ', text)
	text = re.sub(r'\s+', ' ', text)
	text = text.strip()
	
	# Handle potential name reversals (last name, first name vs first name last name)
	parts = text.split()
	if len(parts) >= 2:
		# Try both original order and reversed order
		return ' '.join(sorted(parts))
	return text

class Rider(FirstCyclingObject):
	"""
	Wrapper to load information on riders.

	Attributes
	----------
	ID : int
		The firstycling.com ID for the rider from the URL of their profile page.
	"""
	_default_endpoint = RiderEndpoint

	@classmethod
	def search(cls, query):
		"""
		Search for riders by name using fuzzy matching.

		Parameters
		----------
		query : str
			The search query string

		Returns
		-------
		list
			List of dictionaries containing matching riders with their IDs and details,
			sorted by best match first:
			[
				{'id': int, 'name': str, 'nationality': str, 'team': str},
				...
			]
		"""
		try:
			# Send direct request to the rider search page
			url = f"https://firstcycling.com/rider.php?s={query}"
			response = requests.get(url)
			response.raise_for_status()
			
			# Parse the HTML response
			soup = BeautifulSoup(response.text, 'html.parser')
			
			results = []
			# Normalize the query for better fuzzy matching
			norm_query = normalize(query)
			
			# Find rider tables
			tables = soup.find_all('table', class_='sortTabell')
			
			# Process each table
			for table in tables:
				# Skip header row
				rows = table.find_all('tr')[1:]
				
				for row in rows:
					cells = row.find_all('td')
					if len(cells) >= 3:  # Ensure we have enough cells
						try:
							# Extract rider ID from the URL
							rider_link = cells[0].find('a')
							rider_id = None
							if rider_link and 'href' in rider_link.attrs:
								href = rider_link['href']
								match = re.search(r'rider=(\d+)', href)
								if match:
									rider_id = int(match.group(1))
							
							# Extract rider name and details
							rider_name = cells[0].text.strip()
							nationality = cells[1].text.strip()
							team = cells[2].text.strip()
							
							# Apply fuzzy matching to filter results
							if rider_id is not None and rider_name:
								# Normalize rider name for better matching
								norm_name = normalize(rider_name)
								# Calculate similarity ratio between normalized query and rider name
								ratio = difflib.SequenceMatcher(None, norm_query, norm_name).ratio()
								# Only include riders that have a match ratio above threshold
								if ratio >= 0.6:  # Threshold for considering a match
									results.append({
										'id': rider_id,
										'name': rider_name,
										'nationality': nationality,
										'team': team,
										'match_ratio': ratio  # Store the match ratio for sorting
									})
						except Exception as e:
							# Skip problematic entries
							continue
			
			# Sort results by match ratio in descending order (best matches first)
			results.sort(key=lambda x: x.get('match_ratio', 0), reverse=True)
			
			# Remove match_ratio from final results as it's only used for sorting
			for result in results:
				if 'match_ratio' in result:
					del result['match_ratio']
			
			return results
		except Exception as e:
			print(f"Error in Rider.search: {str(e)}")
			return []

	def _get_response(self, **kwargs):
		return fc.get_rider_endpoint(self.ID, **kwargs)

	def year_results(self, year=None):
		"""
		Get rider details and results for given year.

		Parameters
		----------
		year : int
			Year for which to collect information.
			If None, collects information for latest unloaded year in which rider was active.

		Returns
		-------
		RiderYearResults
		"""
		return self._get_endpoint(endpoint=RiderYearResults, y=year)

	def best_results(self):
		"""
		Get the rider's best results.

		Returns
		-------
		RiderEndpoint
		"""
		return self._get_endpoint(high=1)

	def victories(self, world_tour=None, uci=None):
		"""
		Get the rider's victories.

		Parameters
		----------
		world_tour : bool
			True if only World Tour wins wanted
		uci : bool
			True if only UCI wins wanted

		Returns
		-------
		RiderEndpoint
		"""
		return self._get_endpoint(high=1, k=1, uci=1 if uci else None, wt=1 if world_tour else None)

	def grand_tour_results(self):
		"""
		Get the rider's results in grand tours.

		Returns
		-------
		RiderEndpoint
		"""
		return self._get_endpoint(high=1, k=2)

	def monument_results(self):
		"""
		Get the rider's results in monuments.

		Returns
		-------
		RiderEndpoint
		"""
		return self._get_endpoint(high=1, k=3)

	def team_and_ranking(self):
		"""
		Get the rider's historical teams and rankings.

		Returns
		-------
		RiderEndpoint
		"""
		return self._get_endpoint(stats=1)

	def race_history(self, race_id=None):
		"""
		Get the rider's history at a certain race.

		Parameters
		----------
		race_id : int
			The firstcycling.com ID for the desired race, from the race profile URL.
			If None, loads rider's race history at UCI races.

		Returns
		-------
		RiderEndpoint
		"""
		return self._get_endpoint(stats=1 if not race_id else None, k=1 if not race_id else None, ra=race_id if race_id else None)	

	def one_day_races(self):
		"""
		Get the rider's results at major one-day races.

		Returns
		-------
		RiderEndpoint
		"""
		return self._get_endpoint(stats=1, k=2)

	def stage_races(self):
		"""
		Get the rider's results at major stage races.

		Returns
		-------
		RiderEndpoint
		"""
		return self._get_endpoint(stats=1, k=3)

	def teams(self):
		"""
		Get the rider's historical teams.

		Returns
		-------
		RiderEndpoint
		"""
		return self._get_endpoint(teams=1)