from FirstCyclingAPI.first_cycling_api.rider import Rider
from bs4 import BeautifulSoup
import pandas as pd
import sys

# Get rider ID from command line if provided, otherwise use default
rider_id = int(sys.argv[1]) if len(sys.argv) > 1 else 16672

rider = Rider(rider_id)
response = rider._get_response(high=1, k=3)
soup = BeautifulSoup(response, 'html.parser')

print(f"Checking monument results for rider ID: {rider_id}")

# Find all tables
tables = soup.find_all('table')
print(f'Total tables found: {len(tables)}')

for i, table in enumerate(tables):
    print(f'Table {i} classes: {table.get("class", "[No class]")}')
    rows = table.find_all('tr')
    if rows:
        headers = [th.text.strip() for th in rows[0].find_all(['th', 'td'])]
        print(f'  Headers: {headers}')
        
# Look at the specific table with class 'tablesorter'
table = soup.find('table', class_='tablesorter')
if table:
    try:
        # Attempt to parse the table
        df = pd.read_html(str(table))[0]
        print("\nDataFrame created from table:")
        print(df.head())
        print(f"DataFrame shape: {df.shape}")
    except Exception as e:
        print(f"Error parsing table: {e}")
        
    # Manual extraction
    print("\nManual table extraction:")
    rows = table.find_all('tr')
    for i, row in enumerate(rows[:5]):  # First 5 rows
        cols = row.find_all(['th', 'td'])
        if cols:
            col_texts = [col.text.strip() for col in cols]
            print(f"Row {i}: {col_texts}")
else:
    print("No table with class 'tablesorter' found")

# Check if "No data" text is present
no_data_text = soup.find(string=lambda text: 'No data' in text if text else False)
if no_data_text:
    print("\nFound 'No data' text in the page!")
else:
    print("\nNo 'No data' text found in the page.")

# Check for "monument" or similar text in the page
monument_texts = soup.find_all(string=lambda text: 'monument' in text.lower() if text else False)
print("\nText containing 'monument':")
for text in monument_texts:
    print(f"- {text.strip()}")

# Look at the section titles
section_titles = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])
print("\nSection titles:")
for title in section_titles:
    print(f"- {title.text.strip()}") 