import os, requests, re
from bs4 import BeautifulSoup

SOURCE_NAME = "J-Net21（独立行政法人 中小企業基盤整備機構）"
SOURCE_URL = "https://j-net21.smrj.go.jp/snavi/articles"

def fetch_data():
    try:
        res = requests.get(SOURCE_URL, timeout=20)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.find_all('a', href=re.compile(r'/snavi/articles/\d+'))
        
        data = []
        seen = set()
        for a in links:
            t = a.get_text(strip=True)
            if len(t) > 12 and t not in seen:
                h = a.get('href')
                full_url = h if h.startswith('http') else "https://j-net21.smrj.go.jp" + h
                data.append({"title": t, "link": full_url})
                seen.add(t)
                if len(data) >= 30: break
        return data
    except Exception as e:
        print(f"Error: {e}")
        return []

def generate_html(subsidies):
    # 【最優先事項】収益化リンクの設定（サンプル：あなたのIDに差し替えが必要）
    AD_LINK = "https://www.amazon.co.jp/s?k=補助金+申請" # 補助金関連書籍へのリンク等
    CONSULT_LINK = "#" # 行政書士提携先などのリンク

    list_items = ""
    for item in subsidies:
        list_items += f"""
        <div style="padding:28px 0; border-bottom:1px solid #E2E8F0;">
            <h2 style="font-size:1.15rem; line-height:1.6; margin:0 0 20px 0; color:#1A202C; font-weight:700;">{item['title']}</h2>
            <div style="display:flex; gap:10px;">
                <a href="{item['link']}" target="_blank" style="background-color:#2B6CB0; color:#FFFFFF; padding:12px 24px; text-decoration:none; border-radius:8px; font-size:0.9rem; font-weight:bold;">詳細を確認する</a>
                <a href="{CONSULT_LINK}" style="background-color:#F6AD55; color:#FFFFFF; padding:12px 24px; text-decoration:none; border-radius:8px; font-size:0.9rem; font-weight:bold;">申請の相談をする</a>
            </div>
        </div>"""
    
    html_content = f"""<!DOCTYPE html><html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>補助金速報マネタイズ版</title>
</head>
<body style="max-width:640px; margin:0 auto; background-color:#F8FAFC; padding:40px 20px; font-family:sans-serif; color:#1A202C;">
    <header style="margin-bottom:40px;">
        <h1 style="font-size:1.8rem; margin:0; color:#2B6CB0;">補助金速報</h1>
        <div style="margin-top:20px; padding:15px; background-color:#EBF8FF; border-radius:10px; border:1px solid #BEE3F8;">
            <p style="margin:0; font-size:0.9rem; font-weight:bold; color:#2C5282;">[PR] 申請を有利に進めるために</p>
            <a href="{AD_LINK}" style="color:#2B6CB0; font-size:0.85rem;">最新の補助金攻略本をチェックする →</a>
        </div>
    </header>
    <main style="background-color:#FFFFFF; padding:10px 30px; border-radius:16px; border:1px solid #E2E8F0;">
        {list_items}
    </main>
</body></html>"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    data = fetch_data()
    if data: generate_html(data)
