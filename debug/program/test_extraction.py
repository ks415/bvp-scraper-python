#!/usr/bin/env python3
"""
正しいセレクターでのデータ抽出テスト
"""

import re

import requests
from bs4 import BeautifulSoup


def test_data_extraction():
    """実際のデータ抽出をテスト"""

    print("=== データ抽出テスト ===\n")

    url = "https://www.boatrace.jp/owpc/pc/race/racelist?hd=20250913&jcd=02&rno=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # 現在のセレクターでテーブルを取得
    base_level = 0
    level_element = soup.select_one(
        "body main div div div div:nth-child(2) div:nth-child(3) ul li"
    )
    if level_element:
        base_level = 1

    base_selector = (
        f"body main div div div div:nth-child(2) div:nth-child({base_level + 5}) table"
    )
    tables = soup.select(base_selector)

    if not tables:
        print("テーブルが見つかりません")
        return

    table = tables[0]
    tbodies = table.find_all("tbody")

    print(f"テーブル内のtbody数: {len(tbodies)}")

    # 各艇のデータを抽出
    for boat_number in range(1, 7):
        print(f"\n--- ボート{boat_number} ---")

        if boat_number <= len(tbodies):
            tbody = tbodies[boat_number - 1]  # 0-indexedなので-1

            # 現在のセレクターをテスト
            tbody_selector = f"{base_selector} tbody:nth-child({boat_number})"

            selectors = {
                "boat_number": f"{tbody_selector} tr:nth-child(1) td:nth-child(1)",
                "racer_name": f"{tbody_selector} tr:nth-child(1) td:nth-child(3) div:nth-child(2) a",
                "racer_number_class": f"{tbody_selector} tr:nth-child(1) td:nth-child(3) div:nth-child(1)",
            }

            # 各セレクターをテスト
            for key, selector in selectors.items():
                element = soup.select_one(selector)
                if element:
                    text = element.get_text().strip()
                    print(f"  {key}: '{text}'")
                else:
                    print(f"  {key}: 見つからない")

            # 直接tbodyから抽出してみる
            print("  直接抽出:")
            rows = tbody.find_all("tr")
            if rows:
                first_row = rows[0]
                cells = first_row.find_all("td")

                if len(cells) >= 3:
                    # ボート番号
                    boat_num_text = cells[0].get_text().strip()
                    print(f"    ボート番号: '{boat_num_text}'")

                    # レーサー情報(セル3)
                    racer_cell = cells[2]
                    divs = racer_cell.find_all("div")

                    if len(divs) >= 3:
                        # div1: レーサー番号とクラス
                        number_class_text = divs[0].get_text().strip()
                        print(f"    番号/クラス: '{number_class_text}'")

                        # レーサー番号とクラスを分離
                        if "/" in number_class_text:
                            parts = number_class_text.split("/")
                            racer_number = parts[0].strip()
                            racer_class = parts[1].strip()
                            print(f"      レーサー番号: '{racer_number}'")
                            print(f"      クラス: '{racer_class}'")

                        # div2: レーサー名
                        racer_name = divs[1].get_text().strip()
                        print(f"    レーサー名: '{racer_name}'")

                        # div3: 支部/出身地、年齢、体重
                        personal_info = divs[2].get_text().strip()
                        print(f"    個人情報: '{personal_info}'")

                        # 個人情報を解析
                        lines = [
                            line.strip()
                            for line in personal_info.split("\n")
                            if line.strip()
                        ]
                        if lines:
                            # 支部/出身地
                            if len(lines) >= 1 and "/" in lines[0]:
                                branch_birthplace = lines[0]
                                print(f"      支部/出身地: '{branch_birthplace}'")

                            # 年齢と体重
                            for line in lines:
                                if "歳" in line and "kg" in line:
                                    # 年齢を抽出
                                    age_match = re.search(r"(\d+)歳", line)
                                    weight_match = re.search(r"(\d+\.?\d*)kg", line)

                                    if age_match:
                                        age = age_match.group(1)
                                        print(f"      年齢: {age}")

                                    if weight_match:
                                        weight = weight_match.group(1)
                                        print(f"      体重: {weight}")

                    # その他のセル(成績データ)
                    if len(cells) >= 8:
                        print(f"    F/L/ST: '{cells[3].get_text().strip()}'")
                        print(f"    全国成績: '{cells[4].get_text().strip()}'")
                        print(f"    当地成績: '{cells[5].get_text().strip()}'")
                        print(f"    モーター: '{cells[6].get_text().strip()}'")
                        print(f"    ボート: '{cells[7].get_text().strip()}'")


if __name__ == "__main__":
    test_data_extraction()
