import os
import requests
from datetime import datetime

def run_scraper():
    AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')
    
    headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}
    base_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"

    try:
        # 1. 作用機序: 古いレコードの自動一括削除 (掃除の自動化)
        print("DEBUG: 古いデータを掃除中...")
        res = requests.get(base_url, headers=headers)
        if res.status_code == 200:
            records = res.json().get('records', [])
            for rec in records:
                requests.delete(f"{base_url}/{rec['id']}", headers=headers)

        # 2. 新しいデータの生成
        today = datetime.now().strftime('%m/%d')
        target_topics = [
            {"kw": "IT導入補助金 2026", "label": "【DX推進】IT導入補助金"},
            {"kw": "ものづくり補助金 公募", "label": "【設備投資】ものづくり補助金"},
            {"kw": "事業再構築補助金 最新", "label": "【新事業】事業再構築補助金"},
            {"kw": "省エネ 補助金 自治体", "label": "【コスト削減】省エネ・光熱費補助"},
            {"kw": "創業融資 助成金", "label": "【起業家支援】創業・スタートアップ"}
        ]
        
        new_records = []
        for topic in target_topics:
            search_url = f"https://www.google.com/search?q={topic['kw']}+%E6%96%B0%E7%9D%80"
            new_records.append({
                "fields": {
                    "title": topic['label'],
                    "region": f"更新: {today}",
                    "source_url": search_url
                }
            })

        # 3. 新しいデータの送信
        response = requests.post(base_url, headers=headers, json={"records": new_records})
        if response.status_code == 200:
            print(f"【完遂】掃除と更新が完了しました。")
            
    except Exception as e:
        print(f"【致命的エラー】: {e}")

if __name__ == "__main__":
    run_scraper()
