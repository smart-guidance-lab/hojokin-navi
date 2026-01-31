import os, requests, re
from bs4 import BeautifulSoup

SOURCE_NAME = "J-Net21（独立行政法人 中小企業基盤整備機構）"
SOURCE_URL = "https://j-net21.smrj.go.jp/snavi/articles"

def fetch_clean_data():
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
        print(f"Fetch Error: {e}")
        return []

def generate_html(subsidies):
    list_items = ""
    for item in subsidies:
        # 青色のボタン（信頼性重視）と、装飾を排したタイトル
        list_items += f"""
        <article style="padding:28px 0; border-bottom:1px solid #E2E8F0;">
            <h2 style="font-size:1.15rem; line-height:1.6; margin:0 0 20px 0; color:#2D3748; font-weight:700;">
                {item['title']}
            </h2>
            <div style="display:flex; justify-content:flex-start;">
                <a href="{item['link']}" target="_blank" style="background-color:#2B6CB0; color:#FFFFFF; padding:14px 28px; text-decoration:none; border-radius:8px; font-size:0.95rem; font-weight:bold; box-shadow:0 4px 6px rgba(43,108,176,0.1);">
                    公募要領を確認する
                </a>
            </div>
        </article>"""
    
    html_content = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>補助金DB | J-Net21速報</title></head>
<body style="max-width:640px; margin:0 auto; background-color:#F8FAFC; padding:40px 20px; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color:#1A202C;">
    <header style="margin-bottom:50px; text-align:left;">
        <h1 style="font-size:2rem; margin:0; letter-spacing:-0.04em; color:#2D3748;">補助金速報</h1>
        <p style="font-size:1rem; color:#718096; margin-top:10px;">J-Net21 公募情報：最新30件を同期中</p>
    </header>
    <main style="background-color:#FFFFFF; padding:10px 30px; border-radius:16px; border:1px solid #E2E8F0; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
        {list_items}
    </main>
    <footer style="margin-top:60px; padding-bottom:40px; text-align:center; color:#A0AEC0;">
        <p style="font-size:0.8rem;">出典：{SOURCE_NAME}</p>
        <p style="font-size:0.8rem; margin-top:5px;">24時間ごとに自動更新</p>
    </footer>
</body></html>"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    subsidies = fetch_clean_data()
    if subsidies:
        generate_html(subsidies)
