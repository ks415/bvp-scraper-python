#!/usr/bin/env python3

from bvp_scraper import ResultScraper

# Test the fixed result scraper with winning technique
scraper = ResultScraper()

# Test with the valid data we found
try:
    result = scraper.scrape(
        race_date="2024-09-10",
        race_stadium_number=1,  # Kiryu
        race_number=1,
    )

    print("=== Enhanced Result Scraper Test ===")
    print(f"Race Date: {result.get('race_date')}")
    print(f"Stadium: {result.get('race_stadium_number')}")
    print(f"Race Number: {result.get('race_number')}")

    # Check results
    results = result.get("results", {})
    print(f"\nRace Results ({len(results)} entries):")

    for position in sorted(results.keys()):
        data = results[position]
        print(f"  Position {position}:")
        print(f"    Boat Number: {data.get('boat_number')}")
        print(f"    Racer Name: {data.get('racer_name')}")
        print(f"    Race Time: {data.get('race_time')}")

    # Check race info (決まり手, start info)
    print("\nRace Information:")

    winning_technique = result.get("winning_technique")
    if winning_technique:
        print(f"  決まり手: {winning_technique}")
    else:
        print("  決まり手: No data")

    start_info = result.get("start_info", {})
    if start_info:
        print("  スタート情報:")
        for boat_num in sorted(start_info.keys()):
            timing_data = start_info[boat_num]
            timing = timing_data.get("timing", "N/A")
            special = timing_data.get("special_info", "")
            print(
                f"    艇番{boat_num}: {timing}" + (f" ({special})" if special else "")
            )
    else:
        print("  スタート情報: No data")

    # Check payouts
    print("\nPayouts:")

    payout_types = [
        ("win_payouts", "単勝"),
        ("place_payouts", "複勝"),
        ("exacta_payouts", "2連単"),
        ("quinella_payouts", "2連複"),
        ("quinella_place_payouts", "拡連複"),
        ("trifecta_payouts", "3連単"),
        ("trio_payouts", "3連複"),
    ]

    for payout_key, japanese_name in payout_types:
        payouts = result.get(payout_key, {})
        if payouts:
            print(f"  {japanese_name} ({len(payouts)} entries):")
            for combination, data in payouts.items():
                print(
                    f"    {combination}: ¥{data.get('payout')} (人気: {data.get('popularity')})"
                )
        else:
            print(f"  {japanese_name}: No data")

except Exception as e:
    print(f"Error testing result scraper: {e}")
    import traceback

    traceback.print_exc()
