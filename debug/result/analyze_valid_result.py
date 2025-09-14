#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

# Use the valid race data we found
url = "https://www.boatrace.jp/owpc/pc/race/raceresult?hd=20240910&jcd=01&rno=1"

try:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    print("=== Detailed Analysis of Valid Race Result Page ===")

    tables = soup.find_all("table")
    print(f"Found {len(tables)} tables")

    for i, table in enumerate(tables):
        print(f"\n--- Table {i+1} ---")
        print(f"Classes: {table.get('class', [])}")
        print(f"ID: {table.get('id', 'No ID')}")

        rows = table.find_all("tr")
        print(f"Rows: {len(rows)}")

        for j, row in enumerate(rows):
            cells = row.find_all(["td", "th"])
            if cells:
                cell_texts = []
                for cell in cells:
                    text = cell.get_text(strip=True)
                    cell_texts.append(text if text else "[empty]")
                print(f"  Row {j+1}: {cell_texts}")

    # Look for specific patterns that might indicate race results
    print("\n=== Looking for Race Result Patterns ===")

    # Check for boat numbers (1-6)
    all_text = soup.get_text()
    boat_numbers = []
    for i in range(1, 7):
        if f"{i}艇" in all_text or "号艇" in all_text:
            boat_numbers.append(i)

    print(f"Boat numbers mentioned: {boat_numbers}")

    # Look for time patterns (MM:SS.ff format)
    import re

    time_pattern = r"\d{1,2}:\d{2}\.\d{2}"
    times = re.findall(time_pattern, all_text)
    if times:
        print(f"Race times found: {times}")

    # Look for typical racer name patterns (Japanese names)
    name_pattern = r"[ぁ-んァ-ン一-龯]{2,5}[　 ][ぁ-んァ-ン一-龯]{1,5}"
    names = re.findall(name_pattern, all_text)
    if names:
        print(f"Potential racer names: {names[:10]}")  # First 10

    # Look for elements with specific classes that might contain result data
    result_elements = soup.find_all(
        class_=lambda x: x
        and any(
            keyword in " ".join(x).lower()
            for keyword in ["result", "race", "boat", "racer", "time", "finish"]
        )
    )

    print(f"\nFound {len(result_elements)} elements with result-related classes")
    for i, elem in enumerate(result_elements[:5]):
        print(f"Element {i+1}: {elem.name}, classes: {elem.get('class', [])}")
        print(f"  Text: {elem.get_text(strip=True)[:100]}")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
