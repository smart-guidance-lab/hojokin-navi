import os, requests, re, json
from bs4 import BeautifulSoup
from datetime import datetime

DATA_FILE = "subsidies_db.json"
SOURCE_URL = "https://j-net21.smrj.go.jp/snavi/articles"

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
            if len(title) > 15 and title not in seen_titles:
                href = a.get('href')
                url = href if href.startswith('http') else "https://j-net21.smrj.go.jp" + href
                new_items.append({
                    "title": title, "link": url, 
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
                seen_titles.add(title)

        updated_db = (new_items + db)[:1000]
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_db, f, ensure_ascii=False, indent=2)
        return updated_db
    except: return db

def generate_html(db):
    list_items = ""
    for item in db[:150]:
        list_items += f"""
        <section class="item">
            <time>{item.get('date', '')}</time>
            <h2>{item['title']}</h2>
            <div class="btn-area">
                <a href="{item['link']}" target="_blank" rel="noopener">詳細を確認する</a>
            </div>
        </section>"""

    html_content = f"""<!DOCTYPE html><html lang="ja">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>補助金・助成金データベース</title>
<style>
    :root {{ --bg: #F7FAFC; --surface: #FFFFFF; --text: #2D3748; --accent: #1A365D; --dim: #718096; --border: #E2E8F0; }}
    body {{ margin: 0; font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", "Hiragino Sans", sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; word-wrap: break-word; }}
    .container {{ max-width: 680px; margin: 0 auto; padding: 40px 20px; }}
    header {{ background: var(--surface); padding: 30px; border-radius: 12px; border-left: 8px solid var(--accent); box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 40px; }}
    h1 {{ font-size: 1.6rem; font-weight: 800; color: var(--accent); margin: 0; letter-spacing: -0.02em; }}
    .stats {{ font-size: 0.85rem; color: var(--dim); margin-top: 10px; font-weight: 600; }}
    .item {{ background: var(--surface); padding: 30px; border-radius: 12px; border: 1px solid var(--border); margin-bottom: 20px; transition: transform 0.2s ease; }}
    .item:hover {{ transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }}
    time {{ font-size: 0.8rem; font-weight: 700; color: var(--accent); opacity: 0.8; display: block; }}
    h2 {{ font-size: 1.1rem; font-weight: 700; margin: 10px 0 20px 0; line-height: 1.5; color: var(--text); }}
    .btn-area {{ text-align: right; }}
    a {{ display: inline-block; background: var(--accent); color: #ffffff; text-decoration: none; padding: 12px 30px; font-size: 0.85rem; font-weight: 700; border-radius: 6px; }}
    footer {{ margin-top: 60px; padding: 40px 0; font-size: 0.75rem; color: var(--dim); text-align: center; }}
</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>補助金・助成金アーカイブ</h1>
            <div class="stats">蓄積データ: {len(db)} 件 / 毎日自動更新</div>
        </header>
        <main>{list_items}</main>
        <footer>
            AUTOMATED DATABASE SYSTEM<br>最終更新: {datetime.now().strftime("%Y年%m月%d日 %H:%M")}
        </footer>
    </div>
</body></html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    generate_html(fetch_and_merge())
