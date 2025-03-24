from ..endpoints import ParsedEndpoint
from ..parser import parse_date, parse_table, team_link_to_id, img_to_country_code, link_to_twitter_handle

import pandas as pd
import bs4


class RiderEndpoint(ParsedEndpoint):
	"""
	Rider profile page response. Extends Endpoint.

	Attributes
	----------
	years_active : list[int]
		List of years in which rider was active.
	header_details : dict
		Details from page header, including rider name and external links.
	sidebar_details : dict
		Details from right sidebar, including nation, date of birth, height, and more.
	"""

	def _parse_soup(self):
		self._get_years_active()
		self._get_header_details()
		self._get_sidebar_details()

	def _get_years_active(self):
		# TODO make this more robust, fails when too many active years (e.g. Anna Van Der Breggen)
		try:
			self.years_active = [int(a.text) for a in self.soup.find('p', {'class': "sidemeny2"}).find_all('a')]
		except ValueError:
			print("Warning: could not collect rider's years active.")
			self.years_active = []

	def _get_header_details(self):
		self.header_details = {}
		self.header_details['current_team'] = self.soup.p.text.strip() if self.soup.p.text.strip() else None
		self.header_details['twitter_handle'] = link_to_twitter_handle(self.soup.find('p', {'class': 'left'}).a) if self.soup.find('p', {'class': 'left'}) and self.soup.find('p', {'class': 'left'}).a else None
	
	def _get_sidebar_details(self):
		# TODO Load details from sidebar
		self.sidebar_details = {}


class RiderYearResults(RiderEndpoint):
	"""
	Rider's results in a certain year. Extends RiderEndpoint.

	Attributes
	----------
	year_details : dict
		The year-specific rider details from the page, including the team, division, UCI points, and more.
	results_df : pd.DataFrame
		Table of rider's results from the year.
	"""

	def _parse_soup(self):
		super()._parse_soup()
		self._get_year_details()
		self._get_year_results()

	def _get_year_details(self):
		# Find table with details
		details_table = self.soup.find('table', {'class': 'tablesorter notOddEven'})

		spans = details_table.find_all('span')

		self.year_details = {}
		for span in spans:
			if span.img: # Team details
				self.year_details['Team'] = span.text.split('(')[0].strip()
				self.year_details['Team ID'] = team_link_to_id(span.a)
				self.year_details['Team Country'] = img_to_country_code(span.img)
				self.year_details['Division'] = span.text.split('(')[1].split(')')[0]
			elif 'Ranking' in span.text:
				self.year_details['UCI Ranking'] = int(span.text.split(': ')[1].split()[0])
				self.year_details['UCI Points'] = float(span.text.split('(')[1].split('pts')[0])
			elif 'Wins' in span.text:
				self.year_details['UCI Wins'] = int(span.text.split(': ')[-1])
			elif 'Race days' in span.text:
				self.year_details['Race days'] = int(span.text.split(': ')[-1])
			elif 'Distance' in span.text:
				self.year_details['Distance'] = int(span.text.split(': ')[-1].replace('.', '').split('km')[0])
		

	def _get_year_results(self):
		# Find table with results
		table = self.soup.find('table', {'class': "sortTabell tablesorter"})
		self.results_df = parse_table(table)


class RiderVictories(RiderEndpoint):
	"""
	Rider's victories. Extends RiderEndpoint.

	Attributes
	----------
	results_df : pd.DataFrame
		Table of rider's victories.
	"""

	def _parse_soup(self):
		super()._parse_soup()
		self._get_victories()

	def _get_victories(self):
		# Find table with victories
		table = self.soup.find('table', {'class': "sortTabell tablesorter"})
		if table:
			# Check if the table has "No data" content
			no_data_text = table.get_text().strip()
			if "No data" in no_data_text:
				# Table exists but has no data
				self.results_df = pd.DataFrame()
				return
				
			try:
				# Try to parse using the parse_table function
				self.results_df = parse_table(table)
				if self.results_df is None:
					self.results_df = pd.DataFrame()  # Empty DataFrame if no victories found
			except Exception as e:
				# If there's an error in parsing, handle it by creating a basic DataFrame manually
				print(f"Warning: Error parsing victories table: {str(e)}")
				# Fallback: Try to create a DataFrame directly from the HTML
				try:
					import io
					from dateutil.parser import parse
					
					# Parse the basic table
					html = str(table)
					self.results_df = pd.read_html(io.StringIO(html), decimal=',')[0]
					
					# Check if the table contains "No data"
					if (self.results_df.shape[0] == 1 and 
						"No data" in self.results_df.iloc[0, 0]):
						self.results_df = pd.DataFrame()
						return
					
					# Clean up column names
					# The typical format is: Year | Date | Race | Category
					if 'Date.1' in self.results_df.columns:
						self.results_df.rename(columns={
							'Date': 'Year', 
							'Date.1': 'Date',
							'Unnamed: 2': 'Month_Day'  # This can be blank or contain additional date info
						}, inplace=True)
						
						# Convert Year to string
						self.results_df['Year'] = self.results_df['Year'].astype(str)
						
						# Handle date formatting - combine Year and Date if available
						if 'Month_Day' in self.results_df.columns:
							# Clean Month_Day column (keep only non-NaN values)
							self.results_df = self.results_df.drop('Month_Day', axis=1)
							
						# If Date column has decimal format (e.g., 22.04), treat as MM.DD format
						def format_date(row):
							try:
								if pd.notnull(row['Date']):
									date_str = row['Date']
									if isinstance(date_str, float):
										# Convert float (22.04) to string and handle decimal
										date_parts = str(date_str).split('.')
										if len(date_parts) == 2:
											day = date_parts[0].zfill(2)
											month = date_parts[1].zfill(2)
											return f"{row['Year']}-{month}-{day}"
									return f"{row['Year']}-01-01"  # Default date if format not recognized
								return f"{row['Year']}-01-01"  # Default date if no Date value
							except:
								return f"{row['Year']}-01-01"  # Default for any errors
								
						# Create a formatted date column
						self.results_df['Date_Formatted'] = self.results_df.apply(format_date, axis=1)
						
						# Reorder columns
						col_order = ['Year', 'Date', 'Date_Formatted', 'Race', 'CAT']
						self.results_df = self.results_df[[col for col in col_order if col in self.results_df.columns] + 
														  [col for col in self.results_df.columns if col not in col_order]]
				except Exception as e:
					print(f"Warning: Fallback parsing of victories table failed: {str(e)}")
					# If all else fails, use an empty DataFrame
					self.results_df = pd.DataFrame()
		else:
			# No table found
			self.results_df = pd.DataFrame()  # Empty DataFrame if no table found
