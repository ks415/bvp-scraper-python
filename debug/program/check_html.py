#!/usr/bin/env python3
"""
HTMLの実際の構造を確認するスクリプト
"""

import requests
from bs4 import BeautifulSoup


def check_html_structure():
    """実際のHTMLを取得して構造を確認"""

    print("=== 戸田競艇場 2025-09-13 第1レース HTML構造確認 ===\n")

    # URLを構築
    race_date = "20250913"  # YYYYMMDD形式
    stadium_number = "02"  # 2桁表示
    race_number = "1"

    url = f"https://www.boatrace.jp/owpc/pc/race/racelist?hd={race_date}&jcd={stadium_number}&rno={race_number}"

    print(f"アクセスするURL: {url}")

    try:
        # HTTP要求を送信
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        print(f"HTTPステータス: {response.status_code}")
        print(f"レスポンスサイズ: {len(response.content)} bytes")

        # HTMLを解析
        soup = BeautifulSoup(response.content, "html.parser")

        # タイトルを確認
        title = soup.find("title")
        print(f"ページタイトル: {title.get_text() if title else 'なし'}")

        # メインコンテンツの構造を確認
        main_content = soup.find("main")
        if main_content:
            print("\n=== メインコンテンツの構造 ===")

            # h2タグを探す(レースタイトル)
            h2_tags = main_content.find_all("h2")
            print(f"h2タグ数: {len(h2_tags)}")
            for i, h2 in enumerate(h2_tags[:3]):  # 最初の3つだけ
                print(f"  h2[{i}]: {h2.get_text().strip()}")

            # h3タグを探す(サブタイトル)
            h3_tags = main_content.find_all("h3")
            print(f"h3タグ数: {len(h3_tags)}")
            for i, h3 in enumerate(h3_tags[:3]):
                print(f"  h3[{i}]: {h3.get_text().strip()}")

            # テーブルを探す(レーサー情報)
            tables = main_content.find_all("table")
            print(f"\nテーブル数: {len(tables)}")

            for i, table in enumerate(tables[:2]):  # 最初の2つのテーブルを確認
                print(f"\n--- テーブル {i+1} ---")
                tbody_elements = table.find_all("tbody")
                print(f"  tbody数: {len(tbody_elements)}")

                for j, tbody in enumerate(tbody_elements[:3]):  # 最初の3つだけ
                    print(f"  tbody[{j}]:")
                    rows = tbody.find_all("tr")
                    print(f"    行数: {len(rows)}")

                    if rows:
                        first_row = rows[0]
                        cells = first_row.find_all(["td", "th"])
                        print(f"    最初の行のセル数: {len(cells)}")

                        for k, cell in enumerate(cells[:5]):  # 最初の5セルだけ
                            text = cell.get_text().strip()
                            text = text.replace("\n", " ").replace("\r", " ")
                            if len(text) > 50:
                                text = text[:50] + "..."
                            print(f"      セル[{k}]: {text}")

            # エラーメッセージがないか確認
            error_divs = soup.find_all("div", class_=["error", "message", "notice"])
            if error_divs:
                print("\n=== エラー・メッセージ ===")
                for div in error_divs:
                    print(f"  {div.get_text().strip()}")

            # 「データがありません」などのメッセージを確認
            no_data_indicators = soup.find_all(text=True)
            no_data_messages = [
                text.strip()
                for text in no_data_indicators
                if any(
                    keyword in text
                    for keyword in [
                        "データがありません",
                        "データが見つかりません",
                        "レースが開催されていません",
                        "情報がありません",
                    ]
                )
            ]
            if no_data_messages:
                print("\n=== データ不在メッセージ ===")
                for msg in no_data_messages[:3]:
                    print(f"  {msg}")

        else:
            print("mainタグが見つかりませんでした")
            # 全体のHTMLの一部を確認
            print("\n=== HTML全体の先頭部分 ===")
            print(str(soup)[:1000])

    except requests.RequestException as e:
        print(f"HTTP要求エラー: {e}")
    except Exception as e:
        print(f"予期しないエラー: {e}")
        import traceback

        traceback.print_exc()


def check_current_date():
    """現在日付のデータと比較"""

    print("\n\n=== 現在日付（2025-09-14）のデータ確認 ===\n")

    # 現在日付のスタジアム一覧を取得
    current_date = "20250914"
    url = f"https://www.boatrace.jp/owpc/pc/race/index?hd={current_date}"

    print(f"アクセスするURL: {url}")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        print(f"HTTPステータス: {response.status_code}")

        soup = BeautifulSoup(response.content, "html.parser")

        # タイトルを確認
        title = soup.find("title")
        print(f"ページタイトル: {title.get_text() if title else 'なし'}")

        # 競艇場のリンクを探す
        main_content = soup.find("main")
        if main_content:
            links = main_content.find_all("a", href=True)
            stadium_links = [link for link in links if "jcd=" in link["href"]]

            print(f"\n今日開催される競艇場数: {len(stadium_links)}")

            for link in stadium_links[:5]:  # 最初の5つだけ
                href = link["href"]
                stadium_name = link.get_text().strip()
                print(f"  {stadium_name}: {href}")

    except Exception as e:
        print(f"エラー: {e}")


if __name__ == "__main__":
    check_html_structure()
    check_current_date()
