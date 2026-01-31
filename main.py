import os, requests, re, hashlib, glob
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI

# 構成設定
SOURCE_NAME = "J-Net21（中小機構）"
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

def get_star_rating(rating_input):
    """
    AIの出力を解析し、必ず5文字の★形式に正規化する。
    """
    # 数字だけを抽出
    nums = re.findall(r'\d', str(rating_input))
    count = int(nums[0]) if nums else 3
    count = max(1, min(5, count)) # 1-5の範囲に制限
    return '★' * count + '☆' * (5 - count)

def ai_analyze(title):
    """
    推論を強制し、表記揺れをPython側で吸収する。
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """補助金タイトルの単語から、支援の規模と種類を推論せよ。
【重要】
1. 金額：タイトルから相場を推論（例：50万円以下、100万円〜500万円等）。「参照」は禁止。
2. カテゴリ：製造・建設, IT・DX, 商業・サービス, その他
3. 形式：カテゴリ/対象者/活用内容/金額感/星数(1-5)"""},
                {"role": "user", "content": title}
            ]
        )
        parts = response.choices[0].message.content.split("/")
        # 配列の長さを保証
        while len(parts) < 5: parts.append("3")
        
        return {
            "cat": parts[0].strip(),
            "target": parts[1].strip(),
            "usage": parts[2].strip(),
            "amount": parts[3].strip(),
            "score": get_star_rating(parts[4])
        }
    except:
        return {"cat": "その他", "target": "事業者", "usage": "公式資料を確認", "amount": "10万円〜(推計)", "score": "★★★☆☆"}

def generate_individual_page(item, info, file_id):
    file_path = f"articles/{file_id}.html"
    
    # 金額表記に「資料」という言葉が含まれていたら、推論値に書き換える
    amount_display = info['amount']
    if "資料" in amount_display or "参照" in amount_display:
        amount_display = "10万円〜(タイトルより推計)"

    html = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{item['title']}</title></head>
<body style="max-width:600px; margin:0 auto; padding:40px 20px; font-family:sans-serif; line-height:1.6; color:#333; background:#f4f7f9;">
    <a href="../index.html" style="color:#1a73e8; text-decoration:none; font-size:0.9rem; font-weight:bold;">← 一覧に戻る</a>
    <h1 style="font-size:1.3rem; margin:25px 0; color:#202124; line-height:1.4;">{item['title']}</h1>
    
    <div style="background:#fff; padding:25px; border-radius:15px; box-shadow:0 10px 30px rgba(0,0,0,0.08); margin-bottom:30px; border:1px solid #e0e6ed;">
        <h3 style="margin:0 0 20px 0; font-size:0.95rem; color:#1a73e8; letter-spacing:0.05em;">制度の簡易要約（AI推定）</h3>
        <table style="width:100%; border-collapse:collapse; font-size:0.95rem;">
            <tr style="border-bottom:1px solid #f0f4f8;"><td style="padding:15px 0; color:#6b7280; width:40%;">カテゴリ</td><td style="padding:15px 0; font-weight:bold;">{info['cat']}</td></tr>
            <tr style="border-bottom:1px solid #f0f4f8;"><td style="padding:15px 0; color:#6b7280;">主な対象者</td><td style="padding:15px 0; font-weight:bold;">{info['target']}</td></tr>
            <tr style="border-bottom:1px solid #f0f4f8;"><td style="padding:15px 0; color:#6b7280;">支援対象となる活動</td><td style="padding:15px 0; font-weight:bold;">{info['usage']}</td></tr>
            <tr style="border-bottom:1px solid #f0f4f8;"><td style="padding:15px 0; color:#6b7280;">推定補助金額</td><td style="padding:15px 0; font-weight:bold; color:#d32f2f;">{amount_display}</td></tr>
            <tr><td style="padding:15px 0; color:#6b7280;">AIおすすめ度</td><td style="padding:15px 0; font-weight:bold; color:#f59e0b; letter-spacing:2px; font-family:monospace;">{info['score']}</td></tr>
        </table>
    </div>

    <div style="background:#1a73e8; padding:30px; border-radius:12px; text-align:center;">
        <p style="color:#fff; font-size:0.85rem; margin:0 0 15px 0; font-weight:bold;">正確な要項・期限・申請方法は公式サイトへ</p>
        <a href="{item['link']}" target="_blank" style="display:block; background:#fff; color:#1a73e8; padding:18px; text-decoration:none; border-radius:8px; font-weight:bold; font-size:1.1rem; box-shadow:0 4px 10px rgba(0,0,0,0.1);">J-Net21で一次資料を確認する</a>
    </div>
    <p style="font-size:0.7rem; color:#9ca3af; margin-top:25px; text-align:center;">出典元：{SOURCE_NAME}</p>
</body></html>"""
    with open(file_path, "w", encoding="utf-8") as f: f.write(html)
    return file_path

def generate_html(subsidies):
    cleanup_old_files()
    list_items = ""
    article_urls = []
    for i, item in enumerate(subsidies):
        info = ai_analyze(item['title'])
        file_id = hashlib.md5(item['title'].encode()).hexdigest()[:12] + f"_{i}"
        page_path = generate_individual_page(item, info, file_id)
        article_urls.append(page_path)
        
        list_items += f"""
        <article style="border:1px solid #e5e7eb; padding:25px; margin-bottom:20px; border-radius:16px; background:#fff;">
            <div style="font-size:0.7rem; color:#1a73e8; font-weight:bold; margin-bottom:10px;">{info['cat']} ／ {info['target']}</div>
            <h2 style="font-size:1.05rem; margin:0 0 20px 0; color:#111827; line-height:1.5;">{item['title']}</h2>
            <div style="display:flex; gap:12px;">
                <a href="{page_path}" style="flex:1; text-align:center; background:#f3f4f6; color:#374151; padding:12px; text-decoration:none; border-radius:10px; font-size:0.85rem; font-weight:bold; border:1px solid #d1d5db;">詳細を確認</a>
                <a href="{item['link']}" target="_blank" style="flex:1; text-align:center; background:#1a73e8; color:#fff; padding:12px; text-decoration:none; border-radius:10px; font-size:0.85rem; font-weight:bold;">公式サイト</a>
            </div>
        </article>"""
    
    html_content = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI補助金ナビ</title></head>
<body style="max-width:600px; margin:0 auto; background:#f9fafb; padding:20px; font-family:sans-serif;">
    <header style="margin-bottom:35px; text-align:center;">
        <h1 style="margin:0; font-size:1.7rem; color:#1a73e8;">AI補助金ナビ</h1>
        <div style="display:inline-block; background:#fee2e2; color:#b91c1c; font-size:0.8rem; font-weight:bold; padding:4px 12px; border-radius:20px; margin-top:10px;">毎日AM9:00更新。ブックマーク推奨</div>
    </header>
    <main>{list_items}</main>
</body></html>"""
    with open("index.html", "w", encoding="utf-8") as f: f.write(html_content)
