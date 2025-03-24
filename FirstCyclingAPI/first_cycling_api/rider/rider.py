from ..objects import FirstCyclingObject
from .endpoints import RiderEndpoint, RiderYearResults
from ..api import fc
import requests
from bs4 import BeautifulSoup
import re
import difflib
from typing import List, Dict, Any, Optional

def normalize(text):
	"""
	Normalize rider names for better matching.
	
	Parameters:
		text (str): The text to normalize
		
	Returns:
		str: Normalized text
	"""
	# Convert to lowercase and replace hyphens with spaces, remove excess whitespace
	text = text.lower()
	text = re.sub(r'[-]', ' ', text)
	text = re.sub(r'\s+', ' ', text)
	text = text.strip()
	
	return text

def soundex(name):
	"""
	Simplified implementation of Soundex algorithm, which converts a name into a code
	that represents its pronunciation. This helps with matching names that sound similar.
	
	Parameters:
		name (str): The name to convert
		
	Returns:
		str: The Soundex code
	"""
	# Convert to uppercase and remove non-alphabetic characters
	name = re.sub(r'[^A-Za-z]', '', name.upper())
	
	if not name:
		return ""
		
	# Keep first letter
	first_letter = name[0]
	
	# Replace consonants with digits according to Soundex rules
	name = name[1:]
	name = re.sub(r'[BFPV]', '1', name)
	name = re.sub(r'[CGJKQSXZ]', '2', name)
	name = re.sub(r'[DT]', '3', name)
	name = re.sub(r'[L]', '4', name)
	name = re.sub(r'[MN]', '5', name)
	name = re.sub(r'[R]', '6', name)
	
	# Remove vowels and H, W, Y
	name = re.sub(r'[AEIOUHWY]', '', name)
	
	# Remove repeated digits
	result = ""
	for i in range(len(name)):
		if i == 0 or name[i] != name[i-1]:
			result += name[i]
	
	# Add first letter at the beginning
	result = first_letter + result
	
	# Ensure code is right length (typically 4 characters, including first letter)
	result = result.ljust(4, '0')[:4]
	
	return result
	
def calculate_similarity(query, name):
	"""
	Calculate similarity between a search query and a rider name,
	considering different name formats and parts.
	
	Parameters:
		query (str): The search query
		name (str): The rider name to compare against
		
	Returns:
		float: A similarity score between 0 and 1
	"""
	# Normalize both strings
	norm_query = normalize(query)
	norm_name = normalize(name)
	
	# Basic similarity using sequence matcher
	basic_similarity = difflib.SequenceMatcher(None, norm_query, norm_name).ratio()
	
	# Split into parts and try different combinations
	query_parts = norm_query.split()
	name_parts = norm_name.split()
	
	# If either has no parts, return the basic similarity
	if not query_parts or not name_parts:
		return basic_similarity
	
	# Check for best part matches
	part_similarities = []
	
	# Compare each query part against the full name
	for q_part in query_parts:
		part_sim = difflib.SequenceMatcher(None, q_part, norm_name).ratio()
		part_similarities.append(part_sim)
	
	# Compare full query against each name part
	for n_part in name_parts:
		part_sim = difflib.SequenceMatcher(None, norm_query, n_part).ratio()
		part_similarities.append(part_sim)
	
	# Compare all parts combinations (to handle first/last name variations)
	for q_part in query_parts:
		for n_part in name_parts:
			part_sim = difflib.SequenceMatcher(None, q_part, n_part).ratio()
			part_similarities.append(part_sim)
	
	# Get the best part similarity
	best_part_sim = max(part_similarities) if part_similarities else 0
	
	# Add Soundex comparison for phonetic matching
	soundex_boost = 0
	
	# Apply Soundex to each part combination to handle phonetic variations
	for q_part in query_parts:
		q_soundex = soundex(q_part)
		for n_part in name_parts:
			n_soundex = soundex(n_part)
			if q_soundex == n_soundex and q_soundex:  # Exact Soundex match
				soundex_boost = 0.4  # Significant boost for phonetic matches
				break
		if soundex_boost > 0:
			break
	
	# Combine different matching approaches for final score
	# This weights sequence matching higher, but still allows phonetic matches to influence results
	combined_sim = (basic_similarity + best_part_sim) / 2 + soundex_boost
	
	# Cap at 1.0 for consistency
	return min(combined_sim, 1.0)

class Rider(FirstCyclingObject):
	"""
	Wrapper to load information on riders.

	Attributes
	----------
	ID : int
		The firstycling.com ID for the rider from the URL of their profile page.
	"""
	_default_endpoint = RiderEndpoint
	base_url = "https://firstcycling.com"

	def __init__(self, ID=None):
		"""
		Initialize a Rider object.
		
		Parameters:
			ID (int, optional): The rider ID. Not required for search operations.
		"""
		if ID is not None:
			super().__init__(ID)

	@classmethod
	def search(cls, query: str) -> List[Dict[str, Any]]:
		"""
		Search for riders by name using fuzzy matching.
		
		Parameters:
			query (str): The name to search for
			
		Returns:
			List[Dict[str, Any]]: List of dictionaries containing rider details
								 (id, name, nationality, team), sorted by best match first
		"""
		# Use search.php instead of rider.php for search functionality
		url = f"{cls.base_url}/search.php?s={query}"
		
		try:
			response = requests.get(url)
			soup = BeautifulSoup(response.text, 'html.parser')
			
			# Find all tables with the rider results
			tables = soup.find_all('table')
			
			results = []
			
			# Look for rider links in all tables
			for table in tables:
				rows = table.find_all('tr')
				
				for row in rows:
					cells = row.find_all('td')
					if not cells:
						continue
						
					try:
						# Try to find rider link in any cell
						rider_link = row.find('a', href=lambda href: href and 'rider.php?r=' in href)
						
						if rider_link:
							href = rider_link['href']
							match = re.search(r'rider.php\?r=(\d+)', href)
							
							if match:
								rider_id = int(match.group(1))
								rider_name = rider_link.text.strip()
								
								# Extract nationality and team if available
								nationality = ""
								team = ""
								
								# Find team info (usually in a span with color:grey)
								team_span = row.find('span', style=lambda s: s and 'color:grey' in s)
								if team_span:
									team = team_span.text.strip()
								
								# Look for nationality flag
								flag_span = row.find('span', class_=lambda c: c and 'flag flag-' in c)
								if flag_span and 'class' in flag_span.attrs:
									flag_class = flag_span['class']
									if len(flag_class) >= 2 and flag_class[0] == 'flag':
										nationality = flag_class[1].replace('flag-', '')
								
								# Calculate similarity score using our improved method
								match_ratio = calculate_similarity(query, rider_name)
								
								# Only include riders with a minimum match score
								if match_ratio >= 0.4:  # Lower threshold to catch more variations
									results.append({
										'id': rider_id,
										'name': rider_name,
										'nationality': nationality,
										'team': team,
										'match_ratio': match_ratio
									})
					except Exception as e:
						print(f"Error processing row: {str(e)}")
						continue
			
			# If no direct results, try searching with parts of the query
			if not results and ' ' in query:
				# Extract main parts and try searching with them
				parts = query.strip().split()
				if len(parts) > 1:
					# Try with the first part (usually first name)
					first_part = parts[0]
					if len(first_part) >= 3:  # Only if reasonably long
						first_part_results = cls.search(first_part)
						for r in first_part_results:
							r['match_ratio'] = calculate_similarity(query, r['name']) * 0.9  # Lower confidence
							results.append(r)
					
					# Try with the last part (usually last name)
					last_part = parts[-1]
					if len(last_part) >= 3:  # Only if reasonably long
						last_part_results = cls.search(last_part)
						for r in last_part_results:
							r['match_ratio'] = calculate_similarity(query, r['name']) * 0.9  # Lower confidence
							results.append(r)
			
			# Sort results by match ratio (best matches first)
			results.sort(key=lambda x: x['match_ratio'], reverse=True)
			
			# Remove duplicates based on rider ID
			unique_results = []
			seen_ids = set()
			for r in results:
				if r['id'] not in seen_ids:
					seen_ids.add(r['id'])
					unique_results.append(r)
			
			# Remove match_ratio from the results
			for result in unique_results:
				if 'match_ratio' in result:
					del result['match_ratio']
			
			return unique_results
		
		except Exception as e:
			print(f"Error searching for rider: {str(e)}")
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

	@classmethod
	def profile(cls, rider_id: int) -> Dict[str, Any]:
		response = requests.get(f"{cls.base_url}/rider.php?r={rider_id}")
		soup = BeautifulSoup(response.text, 'html.parser')

		# Basic Info
		profile = {}
		profile["id"] = rider_id

		try:
			h1_tags = soup.select_one("h1")
			if h1_tags:
				profile["name"] = h1_tags.get_text()
		except Exception:
			pass

		# More info
		try:
			info_div = soup.select_one('div.left')
			if info_div:
				info_p = info_div.select_one('p')
				if info_p:
					info_items = info_p.get_text().split('\n')
					for item in info_items:
						if ':' in item:
							key, value = item.split(':', 1)
							profile[key.strip().lower().replace(' ', '_')] = value.strip()
		except Exception:
			pass

		return profile