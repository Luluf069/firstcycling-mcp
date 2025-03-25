from FirstCyclingAPI import search_rider, get_rider_info, search_query_normalizer
from FirstCyclingAPI.utils import normalize_rider_name
from bs4 import BeautifulSoup
import json
import sys
import os

# Update path for fixtures
FIXTURES_PATH = os.path.join(os.path.dirname(__file__), 'fixtures')

def test_search_query(query):
    print(f"\nQuery: {query}")
    print(f"Normalized: {search_query_normalizer(query)}")
    result = search_rider(query=query, print_result=False)
    print(json.dumps(result, indent=2))
    print("\n")
    return result

def test_search():
    """Tests different search queries against the API"""
    
    test_cases = [
        "van der Poel",
        "van aert",
        "tadej poga",
        "alaphilippe",
        "remco even",
        "mads pedersen",
        "sepp kuss"
    ]
    
    for query in test_cases:
        test_search_query(query)

if __name__ == "__main__":
    test_search() 