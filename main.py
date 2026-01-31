import os, requests, re, json
from bs4 import BeautifulSoup
from datetime import datetime

DATA_FILE = "subsidies_db.json"
SOURCE_URL = "https://j-net21.smrj.go.jp/snavi/articles"

# 解析用キーワード（内部処理のみに使用）
KEYWORDS = {"創業": "#E53E3E", "DX": "#3182CE", "省エネ": "#38A169", "展示会": "#805AD5"}

def fetch_and_merge():
    db = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                db = json.load(f)
        except: db = []
    
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
                tags = [k for k in KEYWORDS.keys() if k in title]
                href = a.get('href')
                url = href if href.startswith('http') else "https://j-net21.smrj.go.jp" + href
                new_items.append({
                    "title": title, "link": url, 
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "tags": tags
                })
                seen_titles.add(title)

        updated_db = (new_items + db)[:1000]
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_db, f, ensure_ascii=False, indent=2)
        return updated_db
    except: return db

def generate_html(db):
    list_items = ""
    for item in db[:100]:
        tag_html = "".join([f'<span style="background:{KEYWORDS.get(t, "#718096")}; color:white; padding:1px 6px; border-radius:3px; font-size:0.65rem; margin-right:5px; vertical-align:middle;">{t}</span>' for t in item.get('tags', [])])
        
        list_items += f"""
        <div style="padding:24px 0; border-bottom:1px solid #EDF2F7;">
            <div style="margin-bottom:6px;">{tag_html}</div>
            <p style="font-size:0.75rem; color:#718096; margin:0;">{item.get('date', '')}</p>
            <h2 style="font-size:1.05rem; margin:4px 0 16px 0; color:#1A202C; font-weight:600; line-height:1.5;">{item['title']}</h2>
            <a href="{item['link']}" target="_blank" style="background-color:#1A365D; color:#FFFFFF; padding:10px 24px; text-decoration:none; border-radius:4px; font-size:0.8rem; font-weight:600; display:inline-block;">詳細</a>
        </div>"""

    html_content = f"""<!DOCTYPE html><html lang="ja">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>補助金DB</title></head>
<body style="max-width:600px; margin:0 auto; padding:40px 20px; font-family:-apple-system, sans-serif; background-color:#FFFFFF; color:#1A202C;">
    <header style="margin-bottom:40px; padding-bottom:20px; border-bottom:2px solid #1A202C;">
        <h1 style="margin:0; font-size:1.6rem; font-weight:800; letter-spacing:-0.02em;">補助金データベース</h1>
        <p style="font-size:0.85rem; color:#4A5568; margin-top:8px;">最短アクセス・最短解。余計な加工を省いた情報のストック。</p>
    </header>
    <main>{list_items}</main>
    <footer style="text-align:center; margin-top:60px; color:#A0AEC0; font-size:0.7rem; letter-spacing:0.05em;">
        DATA ACCUMULATION: {len(db)} ITEMS / LAST UPDATE: {datetime.now().strftime("%Y-%m-%d")}
    </footer>
</body></html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    generate_html(fetch_and_merge())
