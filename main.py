import os, hashlib, json, re
from openai import OpenAI

# 構成設定
SOURCE_NAME = "J-Net21"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_visual_meta(amount_str, category):
    """
    Python側で物理的に『色』と『アイコン』を決定し、インラインCSSとして返す。
    """
    # 1. アイコン判定
    icon_map = {"IT・DX": "💻", "製造・建設": "🏗️", "商業・サービス": "🛍️", "その他": "💡"}
    icon = icon_map.get(category, "💡")

    # 2. 数値抽出ロジック（万単位に正規化）
    num_match = re.search(r'(\d+)', amount_str)
    val = int(num_match.group(1)) if num_match else 0
    if "万" not in amount_str and val > 10000:
        val = val // 10000

    # 3. 規模別カラー判定（物理的16進数）
    if val >= 500:
        return icon, "大規模", "#6B46C1" # 紫
    elif val >= 100:
        return icon, "中規模", "#2B6CB0" # 青
    else:
        return icon, "少額支援", "#2F855A" # 緑

def ai_analyze(title):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": '{"cat":"IT・DX or 製造・建設 or 商業・サービス or その他", "amount":"〜〇〇万円"}'},
                {"role": "user", "content": title}
            ]
        )
        d = json.loads(response.choices[0].message.content)
        return d.get("cat", "その他"), d.get("amount", "10万円〜")
    except:
        return "その他", "10万円〜"

def generate_html(subsidies):
    list_items = ""
    for item in subsidies:
        cat, amount = ai_analyze(item['title'])
        icon, b_name, b_color = get_visual_meta(amount, cat)
        
        # 物理的に背景色を強制するインラインCSS
        list_items += f"""
        <article style="border:1px solid #E2E8F0; padding:20px; margin-bottom:15px; border-radius:12px; background-color:#ffffff; box-shadow:0 2px 4px rgba(0,0,0,0.02); overflow:hidden;">
            <div style="display:flex; justify-content:space-between; margin-bottom:12px; align-items:center;">
                <span style="font-size:0.75rem; font-weight:bold; color:#2B6CB0;">{icon} {cat}</span>
                <span style="display:inline-block; background-color:{b_color} !important; color:#ffffff !important; font-size:0.7rem; padding:4px 10px; border-radius:6px; font-weight:bold;">{amount} ({b_name})</span>
            </div>
            <h2 style="font-size:1.05rem; margin:0 0 18px 0; color:#2D3748; line-height:1.5; font-weight:600;">{item['title']}</h2>
            <a href="{item['link']}" target="_blank" style="display:block; text-align:center; background-color:#2B6CB0; color:#ffffff; padding:12px; text-decoration:none; border-radius:8px; font-size:0.9rem; font-weight:bold; transition: opacity 0.2s;">J-Net21で詳細を確認 →</a>
        </article>"""
    
    html_content = f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>AI補助金ナビ</title></head>
<body style="max-width:500px; margin:0 auto; background-color:#F7FAFC; padding:20px; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <header style="margin-bottom:30px; text-align:center;">
        <h1 style="color:#2B6CB0; font-size:1.6rem; letter-spacing:-0.02em; margin:0;">AI補助金ナビ</h1>
        <p style="font-size:0.8rem; color:#718096; margin-top:5px;">J-Net21新着をAIが瞬時に規模選別</p>
    </header>
    <main>{list_items}</main>
    <footer style="margin-top:40px; text-align:center; font-size:0.7rem; color:#A0AEC0; padding-bottom:20px;">
        毎日自動更新 / 出典：独立行政法人 中小企業基盤整備機構
    </footer>
</body></html>"""
    with open("index.html", "w", encoding="utf-8") as f: f.write(html_content)
