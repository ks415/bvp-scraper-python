#!/usr/bin/env python3

import traceback

import requests
from bs4 import BeautifulSoup

from bvp_scraper import ResultScraper

# Test the actual result scraper
scraper = ResultScraper()

# Test with a recent date
try:
    result = scraper.scrape(
        race_date="2024-09-13",
        race_stadium_number=2,  # Toda
        race_number=1,
    )

    print("=== Result Scraper Test ===")
    print(f"Race Date: {result.get('race_date')}")
    print(f"Stadium: {result.get('race_stadium_number')}")
    print(f"Race Number: {result.get('race_number')}")

    # Check results
    results = result.get("results", {})
    print(f"\nFound {len(results)} result entries")

    for position, data in results.items():
        print(f"Position {position}:")
        print(f"  Boat Number: {data.get('boat_number')}")
        print(f"  Racer Name: {data.get('racer_name')}")
        print(f"  Race Time: {data.get('race_time')}")

    # Check payouts
    payouts = result.get("win_payouts", {})
    print(f"\nWin Payouts: {len(payouts)} entries")

except Exception as e:
    print(f"Error testing result scraper: {e}")
    traceback.print_exc()

# Also test with direct URL access
print("\n=== Direct URL Test ===")

url = "https://www.boatrace.jp/owpc/pc/race/raceresult?hd=20240913&jcd=02&rno=1"

try:
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    print(f"URL: {response.url}")
    print(f"Content length: {len(response.content)}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find("title")
        if title:
            print(f"Title: {title.get_text(strip=True)}")

        # Check for error messages or redirects
        body_text = soup.get_text(strip=True)
        if "エラー" in body_text or "error" in body_text.lower():
            print("Error detected in page content")
            print(f"Content sample: {body_text[:200]}")
        elif len(body_text) < 100:
            print("Very short content - possible error page")
            print(f"Full content: {body_text}")
        else:
            print("Page loaded successfully")

except Exception as e:
    print(f"Direct URL test error: {e}")
