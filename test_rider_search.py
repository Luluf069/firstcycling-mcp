from FirstCyclingAPI.first_cycling_api.rider.rider import Rider, normalize, calculate_similarity, soundex

def test_search_query(query):
    print(f"\n{'=' * 60}")
    print(f"Searching for: {query}")
    print(f"Normalized query: {normalize(query)}")
    
    # Show Soundex codes for the query parts
    parts = normalize(query).split()
    if parts:
        print("Soundex codes for query parts:")
        for part in parts:
            print(f"  {part} → {soundex(part)}")
    
    # Perform the search as a class method
    results = Rider.search(query)
    
    # Display results
    print(f"\nFound {len(results)} results")
    
    for i, result in enumerate(results):
        if i >= 5:  # Only show top 5 results if there are many
            remaining = len(results) - 5
            print(f"\n... and {remaining} more results")
            break
            
        print(f"\nResult #{i+1}:")
        print(f"ID: {result.get('id')}")
        print(f"Name: {result.get('name')}")
        print(f"Nationality: {result.get('nationality')}")
        print(f"Team: {result.get('team')}")
        
        # Calculate and show match score and Soundex codes for debugging
        similarity = calculate_similarity(query, result.get('name', ''))
        print(f"Similarity score: {similarity:.2f}")
        
        # Show Soundex codes for the name parts
        name_parts = normalize(result.get('name', '')).split()
        if name_parts:
            print("Soundex codes for name parts:")
            for part in name_parts:
                print(f"  {part} → {soundex(part)}")

def test_search():
    # Test various name formats and misspellings
    queries = [
        "mathieu van der poel",
        "van der poel",
        "mathieu vanderpoele",  # Misspelled
        "poel mathieu",         # Reversed name order
        "matieu van der poel",  # Minor misspelling
        "tadej pogacar",        # Test another rider
        "pogachar",             # Common misspelling
        "pogacar",              # Another variation
        "remco evenepoel",      # Another rider
        "evenpool",             # Significant misspelling
        "vangard",              # Testing Wout van Aert
        "vingegaard",           # Testing Jonas Vingegaard
        "vengegard",            # Misspelled
    ]
    
    for query in queries:
        test_search_query(query)

if __name__ == "__main__":
    test_search() 