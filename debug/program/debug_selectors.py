#!/usr/bin/env python3
"""
CSSセレクターのデバッグスクリプト
実際のHTMLでどのセレクターが機能するかテストする
"""

import requests
from bs4 import BeautifulSoup


def debug_css_selectors():
    """CSSセレクターをデバッグ"""

    print("=== CSSセレクターデバッグ ===\n")

    # HTMLを取得
    url = "https://www.boatrace.jp/owpc/pc/race/racelist?hd=20250913&jcd=02&rno=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # base_levelを判定(現在のコードと同じロジック)
    base_level = 0
    level_element = soup.select_one(
        "body main div div div div:nth-child(2) div:nth-child(3) ul li"
    )
    if level_element:
        base_level = 1

    print(f"base_level: {base_level}")

    # 現在のセレクターをテスト
    current_base_selector = (
        f"body main div div div div:nth-child(2) div:nth-child({base_level + 5}) table"
    )
    print(f"現在のベースセレクター: {current_base_selector}")

    tables = soup.select(current_base_selector)
    print(f"マッチしたテーブル数: {len(tables)}")

    if tables:
        table = tables[0]
        tbodies = table.find_all("tbody")
        print(f"テーブル内のtbody数: {len(tbodies)}")

        # 各tbodyの内容を確認
        for i, tbody in enumerate(tbodies[:3]):  # 最初の3つだけ
            print(f"\n--- tbody[{i+1}] ---")
            rows = tbody.find_all("tr")
            print(f"行数: {len(rows)}")

            if rows:
                first_row = rows[0]
                cells = first_row.find_all("td")
                print(f"最初の行のセル数: {len(cells)}")

                # 各セルの内容を詳しく見る
                for j, cell in enumerate(cells[:8]):  # 最初の8セルだけ
                    text = cell.get_text().strip()
                    print(f"  セル[{j+1}]: '{text}'")

                    # divがあるかチェック
                    divs = cell.find_all("div")
                    if divs:
                        print(f"    div数: {len(divs)}")
                        for k, div in enumerate(divs):
                            div_text = div.get_text().strip()
                            print(f"    div[{k+1}]: '{div_text}'")

                    # aタグがあるかチェック
                    links = cell.find_all("a")
                    if links:
                        for link in links:
                            link_text = link.get_text().strip()
                            print(f"    リンク: '{link_text}'")

    else:
        print("テーブルが見つかりません。別のセレクターを試します。")

        # より広範囲で検索
        all_tables = soup.find_all("table")
        print(f"\nページ全体のテーブル数: {len(all_tables)}")

        for i, table in enumerate(all_tables):
            tbodies = table.find_all("tbody")
            if len(tbodies) >= 6:  # 6艇分のデータがありそうなテーブル
                print(f"\nテーブル{i+1}に6つ以上のtbodyがあります: {len(tbodies)}")

                # このテーブルの場所を特定
                parents = []
                parent = table.parent
                level = 0
                while parent and level < 10:
                    tag_info = f"{parent.name}"
                    if parent.get("class"):
                        tag_info += f".{'.'.join(parent['class'])}"
                    if parent.get("id"):
                        tag_info += f"#{parent['id']}"
                    parents.append(tag_info)
                    parent = parent.parent
                    level += 1

                print(f"  場所: {' > '.join(reversed(parents[:5]))}")

                # 最初のtbodyのデータを確認
                if tbodies:
                    first_tbody = tbodies[0]
                    rows = first_tbody.find_all("tr")
                    if rows:
                        first_row = rows[0]
                        cells = first_row.find_all("td")
                        print(f"  最初のtbodyの最初の行のセル数: {len(cells)}")
                        if len(cells) >= 3:
                            print(f"  セル1: '{cells[0].get_text().strip()}'")
                            print(f"  セル3: '{cells[2].get_text().strip()[:50]}'")


def test_corrected_selectors():
    """修正されたセレクターをテスト"""

    print("\n\n=== 修正セレクターのテスト ===\n")

    url = "https://www.boatrace.jp/owpc/pc/race/racelist?hd=20250913&jcd=02&rno=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # より単純なセレクターでテスト
    test_selectors = [
        "table tbody",
        "main table tbody",
        "body main table tbody",
        "div table tbody",
    ]

    for selector in test_selectors:
        elements = soup.select(selector)
        print(f"セレクター '{selector}': {len(elements)} 個のtbody")

        if len(elements) >= 6:
            print("  → 6艇分のデータがありそうです")

            # 最初のtbodyでレーサー名を抽出してみる
            first_tbody = elements[0]

            # td:nth-child(3)を試す
            name_cell = first_tbody.select_one("tr:nth-child(1) td:nth-child(3)")
            if name_cell:
                print(f"  セル3の内容: '{name_cell.get_text().strip()[:50]}'")

                # レーサー名を含む部分を探す
                text = name_cell.get_text()
                if "/" in text:
                    parts = text.split("/")
                    if len(parts) >= 2:
                        racer_info = parts[1].strip()
                        print(f"  レーサー情報らしき部分: '{racer_info[:30]}'")


if __name__ == "__main__":
    debug_css_selectors()
    test_corrected_selectors()
