#!/usr/bin/env python3
"""
修正版ProgramScraperのテスト
"""

from bvp_scraper import Scraper


def test_fixed_scraper():
    """修正版スクレイパーをテスト"""

    print("=== 修正版ProgramScraperテスト ===\n")

    # 問題のあったデータをテスト
    race_date = "2025-09-13"
    stadium_number = 2  # 戸田競艇場
    race_number = 1  # 第1レース

    try:
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

            print("\nボート情報詳細:")
            boats = race_info.get("boats", {})
            print(f"  取得できたボート数: {len(boats)}")

            for boat_num, boat_data in boats.items():
                print(f"\n  ===== ボート{boat_num} =====")
                print(f"    レーサー名: {boat_data.get('racer_name')}")
                print(f"    レーサー番号: {boat_data.get('racer_number')}")
                print(f"    クラス: {boat_data.get('racer_class_number')}")
                print(f"    年齢: {boat_data.get('racer_age')}")
                print(f"    体重: {boat_data.get('racer_weight')}")
                print(f"    F回数: {boat_data.get('racer_flying_count')}")
                print(f"    L回数: {boat_data.get('racer_late_count')}")
                print(f"    平均ST: {boat_data.get('racer_average_start_timing')}")
                print(f"    全国1着率: {boat_data.get('racer_national_top_1_percent')}")
                print(f"    全国2着率: {boat_data.get('racer_national_top_2_percent')}")
                print(f"    全国3着率: {boat_data.get('racer_national_top_3_percent')}")
                print(f"    当地1着率: {boat_data.get('racer_local_top_1_percent')}")
                print(f"    当地2着率: {boat_data.get('racer_local_top_2_percent')}")
                print(f"    当地3着率: {boat_data.get('racer_local_top_3_percent')}")
                print(
                    f"    モーター番号: {boat_data.get('racer_assigned_motor_number')}"
                )
                print(
                    f"    モーター2着率: {boat_data.get('racer_assigned_motor_top_2_percent')}"
                )
                print(
                    f"    モーター3着率: {boat_data.get('racer_assigned_motor_top_3_percent')}"
                )
                print(f"    ボート番号: {boat_data.get('racer_assigned_boat_number')}")
                print(
                    f"    ボート2着率: {boat_data.get('racer_assigned_boat_top_2_percent')}"
                )
                print(
                    f"    ボート3着率: {boat_data.get('racer_assigned_boat_top_3_percent')}"
                )

                # null値をチェック
                null_fields = []
                for key, value in boat_data.items():
                    if (
                        value is None
                        and key != "racer_branch_number"
                        and key != "racer_birthplace_number"
                    ):
                        null_fields.append(key)

                if null_fields:
                    print(f"    ⚠️  null値フィールド: {', '.join(null_fields)}")
                else:
                    print("    ✅ すべてのフィールドにデータが設定されています")
        else:
            print("指定されたレースのデータが見つかりませんでした")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_fixed_scraper()
