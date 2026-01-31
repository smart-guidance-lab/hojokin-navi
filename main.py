import os, requests, re, json
from bs4 import BeautifulSoup
from datetime import datetime

# 定数定義（物理的な一貫性を担保）
DATA_FILE = "subsidies_db.json"
SOURCE_URL = "https://j-net21.smrj.go.jp/snavi/articles"

def fetch_and_merge():
    print("Starting data fetch...")
    db = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                db = json.load(f)
            print(f"Loaded {len(db)} existing items.")
        except:
            db = []
    
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

        updated_db = new_items + db
        updated_db = updated_db[:1000]
        
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_db, f, ensure_ascii=False, indent=2)
        
        print(f"Update successful. New items: {len(new_items)}. Total items: {len(updated_db)}")
        return updated_db
    except Exception as e:
        print(f"Error during fetch: {e}")
        return db

def generate_html(db):
    print("Generating index.html...")
    
    # リスト項目の生成
    list_items = ""
    for item in db[:50]:
        list_items += f"""
        <div style="padding:20px 0; border-bottom:1px solid #E2E8F0;">
            <p style="font-size:0.8rem; color:#A0AEC0; margin:0;">{item.get('date', '不明')}</p>
            <h2 style="font-size:1.1rem; margin:5px 0 15px 0; font-weight:700;">{item['title']}</h2>
            <a href="{item['link']}" target="_blank" style="background-color:#2B6CB0; color:#FFFFFF; padding:10px 20px; text-decoration:none; border-radius:5px; font-size:0.85rem; font-weight:bold; display:inline-block;">詳細を確認</a>
        </div>"""

    # HTML本文の定義（ここでhtml_contentを定義）
    html_content = f"""<!DOCTYPE html><html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>補助金DB | 資産蓄積中</title>
</head>
<body style="max-width:640px; margin:0 auto; padding:40px 20px; font-family:sans-serif; background-color:#F8FAFC;">
    <header style="background:#FFFFFF; padding:20px; border-radius:10px; margin-bottom:30px; border:1px solid #E2E8F0;">
        <h1 style="margin:0; font-size:1.5rem; color:#2B6CB0;">補助金速報 & データベース</h1>
        <p style="font-size:0.9rem; color:#718096;">現在 {len(db)} 件の情報を蓄積中</p>
    </header>
    <main style="background:#FFFFFF; padding:0 25px; border-radius:10px; border:1px solid #E2E8F0;">
        {list_items}
    </main>
    <footer style="text-align:center; margin-top:20px; color:#A0AEC0; font-size:0.7rem;">
        Last Update: {datetime.now().isoformat()}
    </footer>
</body></html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("HTML generation complete.")

if __name__ == "__main__":
    current_db = fetch_and_merge()
    generate_html(current_db)
