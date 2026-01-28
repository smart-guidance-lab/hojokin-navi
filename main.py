import os
import requests
from datetime import datetime

def run_scraper():
    # 1. 環境変数（Secrets）から鍵を回収
    # 依存関係の最小化：標準ライブラリのみを使用
    AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')
    
    # 2. 収集データ（テスト用サンプル）
    # 本来はここでサイトを巡回しますが、まずは接続確認を優先
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {
        "records": [
            {
                "fields": {
                    "title": f"【自動収集テスト】補助金情報 {now}",
                    "region": "東京都",
                    "source_url": f"https://example.com/test-{datetime.now().timestamp()}"
                }
            }
        ]
    }

    # 3. Airtableへの書き込み（API実行）
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        print(f"DEBUG: Airtableへ送信中... URL: {url}")
        response = requests.post(url, headers=headers, json=data)
        
        # ステップ実行とログ：中間結果を出力し追跡可能にする
        print(f"DEBUG: ステータスコード: {response.status_code}")
        
        if response.status_code == 200:
            print("【成功】Airtableにデータが保存されました。")
        else:
            print(f"【失敗】エラー内容: {response.text}")
            
    except Exception as e:
        # 堅牢なエラー処理：異常値を想定した実装
        print(f"【致命的エラー】通信に失敗しました: {e}")

if __name__ == "__main__":
    run_scraper()
