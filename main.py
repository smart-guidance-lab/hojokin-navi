import os
import requests
from bs4 import BeautifulSoup # 外部ライブラリ：スクレイピング用
from datetime import datetime

def run_scraper():
    # 1. 接続情報の回収
    AIRTABLE_TOKEN = os.getenv('AIRTABLE_TOKEN')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')
    
    # 2. 収集対象（J-Net21 新着情報一覧）
    TARGET_URL = "https://j-net21.smrj.go.jp/snavi/support/index.html"
    
    try:
        print(f"DEBUG: {TARGET_URL} を解析中...")
        res = requests.get(TARGET_URL, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # J-Net21のHTML構造からタイトルとリンクを抽出
        # 作用機序: <ul>内の<li>要素から補助金名とURLを取得
        articles = soup.find_all('li', class_='p-list-support__item')
        
        records = []
        for article in articles[:5]: # 最初は最新5件に限定
            title_tag = article.find('p', class_='p-list-support__title')
            link_tag = article.find('a')
            
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                # URLを絶対パスに変換
                source_url = "https://j-net21.smrj.go.jp" + link_tag.get('href')
                
                records.append({
                    "fields": {
                        "title": title,
                        "region": "全国・広域", # J-Net21は全国網羅のため
                        "source_url": source_url
                    }
                })
        
        # 3. Airtableへの送信
        if not records:
            print("【警告】データが見つかりませんでした。サイト構造が変わった可能性があります。")
            return

        airtable_url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
        headers = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}
        
        response = requests.post(airtable_url, headers=headers, json={"records": records})
        
        if response.status_code == 200:
            print(f"【成功】{len(records)}件の最新情報を保存しました。")
        else:
            print(f"【失敗】Airtableエラー: {response.text}")
            
    except Exception as e:
        print(f"【致命的エラー】: {e}")

if __name__ == "__main__":
    run_scraper()
