#!/usr/bin/env python3
"""
BVP Scraper Python版の使用例
"""

from datetime import date
from bvp_scraper import Scraper

def main():
    """メイン関数"""
    
    print("=== BVP Scraper Python版 使用例 ===\n")
    
    # 日付の設定
    race_date = date(2024, 1, 1)
    stadium_number = 1  # 桐生競艇場
    race_number = 1    # 第1レース
    
    try:
        # 1. 静的メソッドを使用した簡単な方法
        print("1. 静的メソッドでプログラム情報を取得:")
        program_data = Scraper.scrape_programs(race_date, stadium_number, race_number)
        print(f"プログラムデータ: {program_data}")
        
        print("\n2. 静的メソッドでオッズ情報を取得:")
        odds_data = Scraper.scrape_odds(race_date, stadium_number, race_number)
        print(f"オッズデータ: {odds_data}")
        
        # 2. インスタンスを取得して使用
        print("\n3. シングルトンインスタンスを使用:")
        scraper = Scraper.get_instance()
        
        # 予想データを取得
        preview_data = scraper.scrape_previews(race_date, stadium_number, race_number)
        print(f"予想データ: {preview_data}")
        
        # 結果データを取得
        result_data = scraper.scrape_results(race_date, stadium_number, race_number)
        print(f"結果データ: {result_data}")
        
        # 3. 全スタジアム情報を取得
        print("\n4. 全スタジアム情報を取得:")
        stadium_data = Scraper.scrape_stadiums(race_date)
        print(f"スタジアムデータ: {stadium_data}")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")

def example_with_custom_session():
    """カスタムHTTPセッションを使用した例"""
    import requests
    from bvp_scraper import ScraperCore
    
    # カスタムセッションの設定
    session = requests.Session()
    session.headers.update({'User-Agent': 'My Custom Bot 1.0'})
    
    # カスタムセッションでScraperCoreを作成
    scraper_core = ScraperCore(session=session)
    scraper = Scraper.create_instance(scraper_core)
    
    print("=== カスタムセッション使用例 ===")
    # 使用方法は同じ
    data = scraper.scrape_programs('2024-01-01', 1, 1)
    print(f"カスタムセッションでのデータ取得: {data}")

if __name__ == "__main__":
    main()
    print("\n" + "="*50 + "\n")
    example_with_custom_session()