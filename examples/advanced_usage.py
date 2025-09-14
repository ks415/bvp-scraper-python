"""
Advanced usage examples for BVP Scraper Python.

This demonstrates advanced features of the Python port of the original
PHP bvp-scraper library by shimomo.
Original: https://github.com/shimomo/bvp-scraper
"""

from datetime import date, timedelta

import requests

from bvp_scraper import Scraper, ScraperCore


def advanced_configuration_example():
    """Example of advanced scraper configuration."""
    print("Advanced Configuration Example")
    print("-" * 30)

    # Create custom session with specific settings
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Custom Bot 1.0",
            "Accept-Language": "ja-JP,ja;q=0.9",
        }
    )

    # Create scraper core with custom session
    scraper_core = ScraperCore(session)

    # Create scraper instance with custom core
    _scraper = Scraper.create_instance(scraper_core)

    print("Custom scraper instance created with custom session")


def batch_scraping_example():
    """Example of batch scraping multiple dates/stadiums."""
    print("\nBatch Scraping Example")
    print("-" * 22)

    # Define date range
    start_date = date(2024, 1, 1)
    end_date = start_date + timedelta(days=2)

    current_date = start_date
    all_results = {}

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"Processing date: {date_str}")

        try:
            # Get stadiums for the date
            stadiums = Scraper.scrape_stadiums(date_str)

            # Scrape first few stadiums
            for stadium_num in list(stadiums.keys())[:2]:
                print(f"  Processing Stadium {stadium_num}")

                # Scrape programs for all races in this stadium
                programs = Scraper.scrape_programs(date_str, stadium_num)

                # Store results
                if date_str not in all_results:
                    all_results[date_str] = {}
                all_results[date_str][stadium_num] = programs

        except Exception as e:
            print(f"  Error processing {date_str}: {e}")

        current_date += timedelta(days=1)

    print(f"Batch processing completed. Processed {len(all_results)} dates.")


def error_handling_example():
    """Example of proper error handling."""
    print("\nError Handling Example")
    print("-" * 22)

    # Test various error conditions
    test_cases = [
        ("Invalid date", "not-a-date"),
        ("Invalid stadium", "2024-01-01", 99),
        ("Invalid race", "2024-01-01", 1, 99),
    ]

    for description, *args in test_cases:
        try:
            print(f"Testing: {description}")
            result = Scraper.scrape_programs(*args)
            print(f"  Unexpected success: {len(result)} results")
        except ValueError as e:
            print(f"  Expected error caught: {e}")
        except Exception as e:
            print(f"  Unexpected error: {e}")


def data_processing_example():
    """Example of processing scraped data."""
    print("\nData Processing Example")
    print("-" * 23)

    try:
        # Scrape some data
        race_date = "2024-01-01"
        programs = Scraper.scrape_programs(race_date, 1, 1)

        if programs and 1 in programs and 1 in programs[1]:
            race_data = programs[1][1]

            print("Processing race data:")
            print(f"  Date: {race_data.get('race_date')}")
            print(f"  Stadium: {race_data.get('race_stadium_number')}")
            print(f"  Grade: {race_data.get('race_grade_number')}")

            # Process boat data
            if "boats" in race_data:
                boats = race_data["boats"]
                print(f"  Total boats: {len(boats)}")

                # Find most experienced racer (highest class)
                class_map = {"A1": 4, "A2": 3, "B1": 2, "B2": 1}
                best_class_racer = None
                best_class_score = 0

                for _boat_num, boat_data in boats.items():
                    racer_class = boat_data.get("racer_class_number")
                    if racer_class and racer_class in class_map:
                        score = class_map[racer_class]
                        if score > best_class_score:
                            best_class_score = score
                            best_class_racer = boat_data

                if best_class_racer:
                    print(
                        f"  Top class racer: {best_class_racer.get('racer_name')} "
                        f"(Class {best_class_racer.get('racer_class_number')})"
                    )

    except Exception as e:
        print(f"Data processing example failed: {e}")


def main():
    """Run all advanced examples."""
    print("BVP Scraper Python - Advanced Examples")
    print("(Python port of shimomo's PHP bvp-scraper)")
    print("=" * 50)

    # Run examples
    advanced_configuration_example()
    batch_scraping_example()
    error_handling_example()
    data_processing_example()

    print("\n" + "=" * 50)
    print("Advanced examples completed.")
    print("Original PHP library: https://github.com/shimomo/bvp-scraper")


if __name__ == "__main__":
    main()
