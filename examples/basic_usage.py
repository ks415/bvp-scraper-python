"""
Example usage of BVP Scraper Python.

This demonstrates the basic functionality of the Python port of the original 
PHP bvp-scraper library by shimomo.
Original: https://github.com/shimomo/bvp-scraper
"""

from datetime import date
from bvp_scraper import Scraper


def main():
    """Demonstrate basic usage of the scraper."""
    
    print("BVP Scraper Python - Example Usage")
    print("(Python port of shimomo's PHP bvp-scraper)")
    print("=" * 50)
    
    # Example date
    race_date = "2024-01-01"
    
    try:
        # Get stadium information for the date
        print(f"\n1. Getting stadium information for {race_date}...")
        stadiums = Scraper.scrape_stadiums(race_date)
        print(f"Found {len(stadiums)} stadiums with races")
        
        # Show first few stadiums
        for stadium_num, stadium_data in list(stadiums.items())[:3]:
            print(f"  Stadium {stadium_num}: {stadium_data.get('stadium_name', 'Unknown')}")
        
        # Get program for specific race
        print(f"\n2. Getting race program for Stadium 1, Race 1...")
        programs = Scraper.scrape_programs(race_date, 1, 1)
        race_data = programs[1][1]
        
        print(f"  Race Date: {race_data['race_date']}")
        print(f"  Stadium: {race_data['race_stadium_number']}")
        print(f"  Race Number: {race_data['race_number']}")
        print(f"  Race Title: {race_data.get('race_title', 'N/A')}")
        
        if 'boats' in race_data:
            print(f"  Boats: {len(race_data['boats'])}")
            for boat_num, boat_data in race_data['boats'].items():
                racer_name = boat_data.get('racer_name', 'Unknown')
                print(f"    Boat {boat_num}: {racer_name}")
        
        # Get odds for the race
        print(f"\n3. Getting odds for Stadium 1, Race 1...")
        odds = Scraper.scrape_odds(race_date, 1, 1)
        odds_data = odds[1][1]
        
        if 'win_odds' in odds_data:
            print("  Win Odds:")
            for boat_num, odd in odds_data['win_odds'].items():
                print(f"    Boat {boat_num}: {odd}")
        
        # Get preview information
        print(f"\n4. Getting preview information for Stadium 1, Race 1...")
        previews = Scraper.scrape_previews(race_date, 1, 1)
        preview_data = previews[1][1]
        
        print(f"  Weather: {preview_data.get('weather', 'N/A')}")
        print(f"  Wind Speed: {preview_data.get('wind_speed', 'N/A')}")
        
        # Get results
        print(f"\n5. Getting race results for Stadium 1, Race 1...")
        results = Scraper.scrape_results(race_date, 1, 1)
        result_data = results[1][1]
        
        if 'results' in result_data:
            print("  Race Results:")
            for position, boat_result in result_data['results'].items():
                boat_num = boat_result.get('boat_number', 'N/A')
                racer_name = boat_result.get('racer_name', 'Unknown')
                print(f"    {position}位: Boat {boat_num} - {racer_name}")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        print("Note: This is a demonstration and may fail without actual network access")
    
    print("\n" + "=" * 50)
    print("Example completed. Check the documentation for more details.")
    print("Original PHP library: https://github.com/shimomo/bvp-scraper")


if __name__ == "__main__":
    main()