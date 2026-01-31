import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI
import re
import hashlib
import glob

# 設定
SOURCE_NAME = "J-Net21（中小機構）"
SOURCE_URL = "https://j-net21.smrj.go.jp/"
now_dt = datetime.now()
now = now_dt.strftime('%Y年%m月%d日 %H:%M')
sitemap_date = now_dt.strftime('%Y-%m-%d')
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

os.makedirs("articles", exist_ok=True)

def cleanup_old_files():
    """ハッシュ形式以外の旧ファイルを削除"""
    files = glob.glob("articles/*.html")
    for f in files:
        filename = os.path.basename(f)
        if not re.match(r'^[a-f0-9]{12}_\d+\.html$', filename):
            try: os.remove(f)
            except: pass

def ai_analyze(title):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """補助金を分析し、[製造・建設, IT・DX, 商業・サービス, その他]から1つ選び、要約(30字)・金額・スコアを出力せよ。
形式：カテゴリ：要約：金額：スコア："""},
                {"role": "user", "content": title}
            ]
        )
        res = response.choices[0].message.content
        cat = res.split("要約：")[0].replace("カテゴリ：", "").strip()
        summary = res.split("要約：")[1].split("金額：")[0].strip()
        amount = res.split("金額：")[1].split("スコア：")[0].strip()
        score = res.split("スコア：")[1].strip()
        return cat, summary, amount, score
    except: return "その他", "公式資料を確認してください。", "要確認", "★★★"

def generate_individual_page(item, cat, summary, amount, score, file_id):
    file_path = f"articles/{file_id}.html"
    html = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{item['title']}</title></head>
<body style="max-width:600px; margin:0 auto; padding:40px 20px; font-family:sans-serif; line-height:1.6; color:#333; background:#f9f9f9;">
    <a href="../index.html" style="color:#1a73e8; text-decoration:none; font-weight:bold;">← 一覧へ戻る</a>
    <p style="font-size:0.8rem; color:#666; margin-top:20px;">更新日：{now}</p>
    <div style="background:#fff3e0; border:1px solid #ffe0b2; padding:10px; border-radius:5px; margin-bottom:20px; font-size:0.8rem; color:#e65100;">⚠️ 本情報はAIによる自動要約です。正確な募集要項は必ず一次資料をご確認ください。</div>
    <div style="display:inline-block; background:#1a73e8; color:#fff; font-size:0.7rem; padding:2px 8px; border-radius:4px; font-weight:bold;">{cat}</div>
    <h1 style="font-size:1.4rem; margin:10px 0; line-height:1.4;">{item['title']}</h1>
    <div style="background:#fff; padding:20px; border-radius:10px; border:1px solid #eee; margin-bottom:20px;">
        <p style="color:#e65100; font-weight:bold; font-size:1.2rem; margin:0;">金額：{amount}</p>
        <p style="margin:10px 0 0 0; color:#555;">おすすめ度：{score}</p>
    </div>
    <p style="font-size:1rem; color:#333;">{summary}</p>
    <div style="margin-top:40px; padding:25px; background:#fff; border:2px solid #34a853; border-radius:12px; text-align:center;">
        <p style="font-size:0.9rem; margin:0 0 15px 0; color:#202124; font-weight:bold;">📍 出典元で詳しく見る（外部サイト）</p>
        <a href="{item['link']}" target="_blank" style="display:block; background:#34a853; color:#fff; padding:18px; text-decoration:none; border-radius:8px; font-weight:bold; font-size:1.1rem; box-shadow: 0 4px 6px rgba(52,168,83,0.2);">公式サイトで詳細を確認</a>
        <p style="font-size:0.75rem; color:#5f6368; margin-top:10px;">出典：{SOURCE_NAME}</p>
    </div>
</body></html>"""
    with open(file_path, "w", encoding="utf-8") as f: f.write(html)
    return file_path

def generate_html(subsidies):
    cleanup_old_files()
    list_items = ""
    article_urls = []
    for i, item in enumerate(subsidies):
        cat, summary, amount, score = ai_analyze(item['title'])
        file_id = hashlib.md5(item['title'].encode()).hexdigest()[:12] + f"_{i}"
        page_path = generate_individual_page(item, cat, summary, amount, score, file_id)
        article_urls.append(page_path)
        
        list_items += f"""
        <article style="border: 1px solid #dadce0; padding: 20px; margin-bottom: 20px; border-radius: 12px; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <div style="font-size:0.65rem; color:#1a73e8; font-weight:bold; margin-bottom:8px; letter-spacing:0.05em;">【{cat}】</div>
            <h2 style="font-size:1.05rem; margin:0 0 12px 0; color:#202124; line-height:1.5;">{item['title']}</h2>
            <p style="font-size:0.9rem; color:#5f6368; margin-bottom:18px; line-height:1.6;">{summary}</p>
            <div style="display:flex; gap:12px;">
                <a href="{page_path}" style="flex:1; text-align:center; border:2px solid #1a73e8; color:#1a73e8; padding:12px; text-decoration:none; border-radius:8px; font-size:0.85rem; font-weight:bold;">AI要約を読む</a>
                <a href="{item['link']}" target="_blank" style="flex:1.2; text-align:center; background:#34a853; color:#fff; padding:12px; text-decoration:none; border-radius:8px; font-size:0.85rem; font-weight:bold; box-shadow: 0 2px 4px rgba(52,168,83,0.15);">公式サイトへ</a>
            </div>
        </article>"""
    
    html_content = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="google-site-verification" content="qDKunZB9hZN753KuLftIbJUXeWBi3bA-HfSS-gej1KA" />
<title>AI補助金ナビ | 最新の補助金情報をAIが要約</title></head>
<body style="max-width: 600px; margin: 0 auto; background: #f8f9fa; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <header style="padding: 20px 0; border-bottom: 2px solid #1a73e8; margin-bottom: 30px;">
        <h1 style="font-size:1.6rem; margin:0; color:#202124;">AI補助金ナビ</h1>
        <p style="font-size:0.8rem; color:#5f6368; margin:5px 0 0 0;">出典：<a href="{SOURCE_URL}" target="_blank" style="color:#1a73e8;">{SOURCE_NAME}</a> の最新データ</p>
    </header>
    <main>{list_items}</main>
    <footer style="text-align:center; padding:40px 0; color:#70757a; font-size:0.75rem;">
        <p>&copy; 2026 AI補助金ナビ. 全ての要約はAIによって生成されています。</p>
    </footer>
</body></html>"""
    
    with open("index.html", "w", encoding="utf-8") as f: f.write(html_content)
    
    # Sitemap生成
    base_url = "https://smart-guidance-lab.github.io/hojokin-navi/"
    s_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    s_lines.append(f'  <url><loc>{base_url}index.html</loc><lastmod>{sitemap_date}</lastmod><priority>1.0</priority></url>')
    for u in article_urls: s_lines.append(f'  <url><loc>{base_url}{u}</loc><lastmod>{sitemap_date}</lastmod><priority>0.8</priority></url>')
    s_lines.append('</urlset>')
    with open("sitemap.xml", "w", encoding="utf-8") as f: f.write("\n".join(s_lines))

def fetch_data():
    url = "https://j-net21.smrj.go.jp/snavi/articles"
    res = requests.get(url, timeout=30)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, 'html.parser')
    all_links = soup.find_all('a', href=re.compile(r'/snavi/articles/\d+'))
    data = []
    seen = set()
    for a in all_links:
        t = a.get_text(strip=True)
        h = a.get('href')
        if len(t) > 5 and t not in seen:
            f_url = h if h.startswith('http') else "https://j-net21.smrj.go.jp" + h
            data.append({"title": t, "link": f_url})
            seen.add(t)
            if len(data) >= 10: break
    return data

if __name__ == "__main__":
    try:
        subsidies = fetch_data()
        if subsidies: generate_html(subsidies)
    except Exception as e: print(f"Error: {e}")
