import os, requests, re, json
from bs4 import BeautifulSoup
from datetime import datetime

DATA_FILE = "subsidies_db.json"
SOURCE_URL = "https://j-net21.smrj.go.jp/snavi/articles"

def fetch_and_merge():
    print("Starting data fetch...") # ログ出力開始
    
    # 1. 既存データの読み込み（なければ空）
    db = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                db = json.load(f)
            print(f"Loaded {len(db)} existing items.")
        except:
            db = []
    
    # 2. 新着データの取得
    try:
        res = requests.get(SOURCE_URL, timeout=20)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.find_all('a', href=re.compile(r'/snavi/articles/\d+'))
        
        seen_titles = {item['title'] for item in db}
        new_items = []
        
        for a in links:
            title = a.get_text(strip=True)
            if len(title) > 12 and title not in seen_titles:
                href = a.get('href')
                url = href if href.startswith('http') else "https://j-net21.smrj.go.jp" + href
                new_items.append({
                    "title": title, 
                    "link": url, 
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
                seen_titles.add(title)

        # 新着を先頭に追加してマージ
        updated_db = new_items + db
        updated_db = updated_db[:1000] # 最大1000件
        
        # 3. 物理ファイルへの書き出し（必ず実行）
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_db, f, ensure_ascii=False, indent=2)
        
        print(f"Update successful. New items: {len(new_items)}. Total items: {len(updated_db)}")
        return updated_db
    except Exception as e:
        print(f"Error during fetch: {e}")
        return db

def generate_html(db):
    print("Generating index.html...")
    # 前回のHTML生成ロジックをここに含める
    # (中略：前回のHTML生成コード)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("\n" + html_content)
    print("HTML generation complete.")

if __name__ == "__main__":
    current_db = fetch_and_merge()
    generate_html(current_db)
