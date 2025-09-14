#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

# Test URL for race result - using a more recent date
url = "https://www.boatrace.jp/owpc/pc/race/raceresult?hd=20240913&jcd=02&rno=1"

try:
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    print("=== Response Info ===")
    print(f"Status Code: {response.status_code}")
    print(f"Content Length: {len(response.content)}")
    print(f"Content Type: {response.headers.get('content-type', 'Unknown')}")

    print("\n=== HTML Structure Analysis ===")

    # Check if it's a valid HTML page
    title = soup.find("title")
    if title:
        print(f"Page Title: {title.get_text(strip=True)}")

    # Look for main content
    main_content = soup.find("main")
    if main_content:
        print("Found main element")
    else:
        print("No main element found")

    # Look for all div elements
    all_divs = soup.find_all("div")
    print(f"Total div elements: {len(all_divs)}")

    # Look for result table or section
    result_sections = soup.find_all("table")
    print(f"Found {len(result_sections)} tables")

    # Check for alternative structures
    print("\n=== Alternative Structures ===")

    # Look for ul/li structures
    ul_elements = soup.find_all("ul")
    print(f"Found {len(ul_elements)} ul elements")

    # Look for spans, divs with classes
    class_patterns = ["result", "boat", "racer", "time", "finish", "order"]
    for pattern in class_patterns:
        elements = soup.find_all(
            class_=lambda x, p=pattern: x and p in " ".join(x).lower()
        )
        if elements:
            print(f"Found {len(elements)} elements with class containing '{pattern}'")

    # Print first few div elements to see structure
    print("\n=== First 10 Div Elements ===")
    for i, div in enumerate(all_divs[:10]):
        classes = div.get("class", [])
        div_id = div.get("id", "")
        text = div.get_text(strip=True)[:50]
        print(f"Div {i+1}: class={classes}, id={div_id}, text={text}")

    # Check if we're getting redirected or error page
    print("\n=== Page Content Sample ===")
    body_text = soup.get_text(strip=True)[:500]
    print(f"Body text sample: {body_text}")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
