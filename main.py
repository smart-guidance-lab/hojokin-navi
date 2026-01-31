import os, requests, re, hashlib, glob
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI

SOURCE_NAME = "J-Net21（独立行政法人 中小企業基盤整備機構）"
SOURCE_URL = "https://j-net21.smrj.go.jp/"
now_dt = datetime.now()
now = now_dt.strftime('%Y年%m月%d日 %H:%M')
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

os.makedirs("articles", exist_ok=True)

def cleanup_old_files():
    for f in glob.glob("articles/*.html"):
        if not re.match(r'^[a-f0-9]{12}_\d+\.html$', os.path.basename(f)):
            try: os.remove(f)
            except: pass

def ai_analyze(title):
    """論理的推論を強制し『一次資料参照』を極小化するプロンプト"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """補助金タイトルを分析し、以下の5項目を『必ず』埋めよ。
1.カテゴリ:[製造・建設, IT・DX, 商業・サービス, その他]
2.対象者:(例:小規模事業者, 全業種など)
3.活用内容:(15文字以内の具体的な具体例)
4.概算金額:(金額不明な場合もタイトルから規模を推測し「〜50万円」「100万円〜」等と記載せよ。どうしても無理な場合のみ「要詳細確認」)
5.推奨度:(★1-5)
形式：カテゴリ/対象者/活用内容/概算金額/推奨度"""},
                {"role": "user", "content": title}
            ]
        )
        res = response.choices[0].message.content.split("/")
        if len(res) < 5: return "その他", "要確認", "公式ページを参照", "調査中", "★★★"
        return res[0], res[1], res[2], res[3], res[4]
    except:
        return "その他", "要確認", "公式ページを参照", "調査中", "★★★"

def generate_individual_page(item, cat, target, usage, amount, score, file_id):
    file_path = f"articles/{file_id}.html"
    html = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{item['title']}</title></head>
<body style="max-width:600px; margin:0 auto; padding:40px 20px; font-family:sans-serif; line-height:1.6; color:#333; background:#f4f7f9;">
    <a href="../index.html" style="color:#1a73e8; text-decoration:none; font-size:0.9rem;">← 一覧に戻る</a>
    <h1 style="font-size:1.4rem; margin:20px 0; color:#202124; line-height:1.4;">{item['title']}</h1>
    
    <div style="background:#fff; padding:25px; border-radius:15px; box-shadow:0 10px 25px rgba(0,0,0,0.05); margin-bottom:30px; border:1px solid #e0e6ed;">
        <h3 style="margin:0 0 20px 0; font-size:1rem; color:#1a73e8; display:flex; align-items:center;">🔍 AI解析レポート</h3>
        <table style="width:100%; border-collapse:collapse; font-size:0.95rem;">
            <tr style="border-bottom:1px solid #f0f4f8;"><td style="padding:15px 0; color:#6b7280; width:40%;">カテゴリ</td><td style="padding:15px 0; font-weight:bold;">{cat}</td></tr>
            <tr style="border-bottom:1px solid #f0f4f8;"><td style="padding:15px 0; color:#6b7280;">対象ターゲット</td><td style="padding:15px 0; font-weight:bold;">{target}</td></tr>
            <tr style="border-bottom:1px solid #f0f4f8;"><td style="padding:15px 0; color:#6b7280;">想定される活用</td><td style="padding:15px 0; font-weight:bold;">{usage}</td></tr>
            <tr style="border-bottom:1px solid #f0f4f8;"><td style="padding:15px 0; color:#6b7280;">補助金額（推測）</td><td style="padding:15px 0; font-weight:bold; color:#d32f2f; font-size:1.1rem;">{amount}</td></tr>
            <tr><td style="padding:15px 0; color:#6b7280;">AIおすすめ度</td><td style="padding:15px 0; font-weight:bold; color:#f59e0b; font-size:1.2rem;">{score}</td></tr>
        </table>
    </div>

    <div style="background:#1a73e8; padding:30px; border-radius:15px; text-align:center; box-shadow:0 8px 20px rgba(26,115,232,0.3);">
        <p style="color:#fff; font-size:0.9rem; margin:0 0 15px 0; opacity:0.9;">正確な募集要項・申請期限は公式サイトへ</p>
        <a href="{item['link']}" target="_blank" style="display:block; background:#fff; color:#1a73e8; padding:18px; text-decoration:none; border-radius:10px; font-weight:bold; font-size:1.1rem;">J-Net21で一次資料を確認する</a>
    </div>
    <p style="font-size:0.7rem; color:#9ca3af; margin-top:25px; text-align:center; line-height:1.4;">※本内容はタイトルからAIが推論した参考情報です。<br>出典元：{SOURCE_NAME}</p>
</body></html>"""
    with open(file_path, "w", encoding="utf-8") as f: f.write(html)
    return file_path

def generate_html(subsidies):
    cleanup_old_files()
    list_items = ""
    article_urls = []
    for i, item in enumerate(subsidies):
        cat, target, usage, amount, score = ai_analyze(item['title'])
        file_id = hashlib.md5(item['title'].encode()).hexdigest()[:12] + f"_{i}"
        page_path = generate_individual_page(item, cat, target, usage, amount, score, file_id)
        article_urls.append(page_path)
        
        list_items += f"""
        <article style="border:1px solid #e5e7eb; padding:25px; margin-bottom:20px; border-radius:16px; background:#fff; transition: transform 0.2s;">
            <div style="font-size:0.7rem; color:#1a73e8; font-weight:bold; margin-bottom:10px; text-transform:uppercase; letter-spacing:0.05em;">{cat} ／ {target}</div>
            <h2 style="font-size:1.1rem; margin:0 0 20px 0; color:#111827; line-height:1.5;">{item['title']}</h2>
            <div style="display:flex; gap:12px;">
                <a href="{page_path}" style="flex:1; text-align:center; background:#f3f4f6; color:#374151; padding:14px; text-decoration:none; border-radius:10px; font-size:0.85rem; font-weight:bold; border:1px solid #d1d5db; box-shadow:0 2px 4px rgba(0,0,0,0.05);">詳細解析をチェック</a>
                <a href="{item['link']}" target="_blank" style="flex:1; text-align:center; background:#1a73e8; color:#fff; padding:14px; text-decoration:none; border-radius:10px; font-size:0.85rem; font-weight:bold; box-shadow:0 4px 10px rgba(26,115,232,0.2);">公式サイトへ</a>
            </div>
        </article>"""
    
    html_content = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI補助金ナビ | 最速・最短で公的支援を把握</title></head>
<body style="max-width:600px; margin:0 auto; background:#f9fafb; padding:20px; font-family:-apple-system,BlinkMacSystemFont,sans-serif;">
    <header style="margin-bottom:35px; text-align:center;">
        <h1 style="margin:0; font-size:1.8rem; color:#1a73e8; letter-spacing:-0.02em;">AI補助金ナビ</h1>
        <div style="display:inline-block; background:#fee2e2; color:#b91c1c; font-size:0.8rem; font-weight:bold; padding:4px 12px; border-radius:20px; margin-top:10px;">毎日AM9:00更新。ブックマーク推奨</div>
    </header>
    <main>{list_items}</main>
</body></html>"""
    with open("index.html", "w", encoding="utf-8") as f: f.write(html_content)
