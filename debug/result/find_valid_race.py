#!/usr/bin/env python3


import requests
from bs4 import BeautifulSoup


def test_race_result_url(date_str, stadium, race_num):
    """Test if a race result URL returns valid data"""
    url = f"https://www.boatrace.jp/owpc/pc/race/raceresult?hd={date_str}&jcd={stadium:02d}&rno={race_num}"

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        body_text = soup.get_text(strip=True)
        has_data = "データがありません" not in body_text

        print(f"Date: {date_str}, Stadium: {stadium}, Race: {race_num}")
        print(f"  URL: {url}")
        print(f"  Status: {response.status_code}")
        print(f"  Has Data: {has_data}")

        if has_data:
            # Look for result data
            print(f"  Content length: {len(body_text)}")

            # Look for tables or result structures
            tables = soup.find_all("table")
            divs_with_result = soup.find_all(
                "div", class_=lambda x: x and "result" in " ".join(x).lower()
            )

            print(f"  Tables found: {len(tables)}")
            print(f"  Result divs: {len(divs_with_result)}")

            if tables:
                print("  First table classes:", tables[0].get("class", []))
                rows = tables[0].find_all("tr")
                print(f"  First table rows: {len(rows)}")

                # Sample first few cells
                if rows:
                    for i, row in enumerate(rows[:3]):
                        cells = row.find_all(["td", "th"])
                        cell_texts = [cell.get_text(strip=True) for cell in cells[:5]]
                        print(f"    Row {i+1}: {cell_texts}")

        print()
        return has_data

    except Exception as e:
        print(f"Error testing {date_str}: {e}")
        return False


# Test recent dates to find valid race data
print("=== Testing Recent Dates for Valid Race Data ===")

# Test different dates and stadiums
test_dates = [
    "20240910",
    "20240911",
    "20240912",
    "20240913",
    "20240914",
    "20240915",
    "20240916",
    "20240917",
    "20240918",
    "20240919",
    "20240920",
]

# Test multiple stadiums (commonly active ones)
stadiums = [1, 2, 3, 4, 5]  # Different stadiums

found_valid = False
for date_str in test_dates:
    for stadium in stadiums:
        for race_num in [1, 2]:  # Test first two races
            if test_race_result_url(date_str, stadium, race_num):
                found_valid = True
                print(
                    f"*** FOUND VALID DATA: {date_str}, Stadium {stadium}, Race {race_num} ***"
                )
                break
        if found_valid:
            break
    if found_valid:
        break

if not found_valid:
    print("No valid race data found in tested range.")
