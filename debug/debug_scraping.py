#!/usr/bin/env python3
"""
問題の調査用スクリプト
2025-09-13 戸田(競艇場番号2)第1レースのデータ取得をテストする
"""

from datetime import date

from bvp_scraper import Scraper


def test_debug_scraping():
    """問題のデータをテストして詳細を確認"""

    print("=== 2025-09-13 戸田 第1レース データ取得テスト ===\n")

    # 問題の日付・競艇場・レース番号
    race_date = "2025-09-13"
    stadium_number = 2  # 戸田競艇場
    race_number = 1  # 第1レース

    try:
        # プログラム情報を取得
        print("プログラム情報を取得中...")
        program_data = Scraper.scrape_programs(race_date, stadium_number, race_number)

        if (
            stadium_number in program_data
            and race_number in program_data[stadium_number]
        ):
            race_info = program_data[stadium_number][race_number]

            print("レース基本情報:")
            print(f"  日付: {race_info.get('race_date')}")
            print(f"  競艇場: {race_info.get('race_stadium_number')}")
            print(f"  レース番号: {race_info.get('race_number')}")
            print(f"  タイトル: {race_info.get('race_title')}")
            print(f"  サブタイトル: {race_info.get('race_subtitle')}")
            print(f"  距離: {race_info.get('race_distance')}")
            print(f"  グレード: {race_info.get('race_grade_number')}")
            print(f"  締切時間: {race_info.get('race_closed_at')}")

            print("\nボート情報:")
            boats = race_info.get("boats", {})
            print(f"  ボート数: {len(boats)}")

            for boat_num, boat_data in boats.items():
                print(f"\n  ボート{boat_num}:")
                print(f"    レーサー名: {boat_data.get('racer_name')}")
                print(f"    レーサー番号: {boat_data.get('racer_number')}")
                print(f"    クラス: {boat_data.get('racer_class_number')}")
                print(f"    年齢: {boat_data.get('racer_age')}")
                print(f"    体重: {boat_data.get('racer_weight')}")
        else:
            print("指定されたレースのデータが見つかりませんでした")
            print(f"利用可能な競艇場: {list(program_data.keys())}")
            if stadium_number in program_data:
                print(
                    f"競艇場{stadium_number}の利用可能なレース: {list(program_data[stadium_number].keys())}"
                )

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()


def test_current_date():
    """現在日付周辺のデータもテストして比較"""

    print("\n=== 現在日付周辺のデータテスト ===\n")

    # 現在日付(今日は2025年9月14日)
    current_date = date(2025, 9, 14)

    try:
        # スタジアム情報を取得
        print("今日のスタジアム情報を取得中...")
        stadium_data = Scraper.scrape_stadiums(current_date)

        print(f"今日開催される競艇場数: {len(stadium_data)}")
        for stadium_num, info in list(stadium_data.items())[:3]:  # 最初の3つだけ表示
            print(f"  競艇場{stadium_num}: {info.get('stadium_name', 'Unknown')}")

        # 昨日のデータもテスト
        yesterday = date(2025, 9, 13)
        print(f"\n昨日({yesterday})のスタジアム情報を取得中...")
        yesterday_stadium_data = Scraper.scrape_stadiums(yesterday)

        print(f"昨日開催された競艇場数: {len(yesterday_stadium_data)}")
        for stadium_num, info in list(yesterday_stadium_data.items())[:3]:
            print(f"  競艇場{stadium_num}: {info.get('stadium_name', 'Unknown')}")

        # 戸田競艇場が昨日開催されていたかチェック
        if 2 in yesterday_stadium_data:
            print("\n昨日戸田競艇場は開催されていました")
            # 戸田競艇場の第1レースをテスト
            print("戸田競艇場の第1レースを取得してみます...")
            program_data = Scraper.scrape_programs(yesterday, 2, 1)
            if 2 in program_data and 1 in program_data[2]:
                race_info = program_data[2][1]
                boats = race_info.get("boats", {})
                racer_1 = boats.get(1, {})
                print(f"  1号艇レーサー名: {racer_1.get('racer_name')}")
                print(f"  1号艇レーサー番号: {racer_1.get('racer_number')}")
            else:
                print("  レースデータの取得に失敗しました")
        else:
            print("\n昨日戸田競艇場は開催されていませんでした")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_debug_scraping()
    test_current_date()
