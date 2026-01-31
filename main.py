import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from openai import OpenAI

# 物理定数・単位の厳守: 日本標準時
now = datetime.now().strftime('%Y年%m月%d日 %H:%M')
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def ai_summarize(title):
    """
    OpenAI APIを用いて、補助金タイトルから『メリット・対象・緊急性』を推論要約する。
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "補助金情報のタイトルを元に、経営者が知るべき要点を3箇条（各20文字以内）で出力せよ。形式：・項目名：内容"},
                {"role": "user", "content": title}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.replace('\n', '<br>')
    except Exception as e:
        print(f"AI Error: {e}")
        return "・詳細は公式URLを確認してください。"

def generate_html(subsidies):
    google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSddIW5zNLUuZLyQWIESX0EOZWZUM3dGM6pdW9Luw20YTiEuwg/viewform"
    
    list_items = ""
    for item in subsidies:
        summary = ai_summarize(item['title'])
        list_items += f"""
        <article style="border: 1px solid #eee; padding: 25px; margin-bottom: 25px; border-radius: 15px; background: #fff; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h2 style="color: #1a73e8; margin-top: 0; font-size: 1.3rem;">{item['title']}</h2>
            <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 15px 0; font-size: 0.95rem; line-height: 1.8;">
                <strong style="color: #d93025;">▼ 3秒でわかる要点</strong><br>
                {summary}
            </div>
            <div style="display: flex; gap: 10px;">
                <a href="{item['link']}" target="_blank" style="flex: 1; text-align: center; border: 1px solid #dadce0; padding: 12px; text-decoration: none; border-radius: 8px; color: #3c4043; font-weight: bold;">一次資料</a>
                <a href="{google_form_url}" target="_blank" style="flex: 1; text-align: center; background: #1a73e8; color: white; padding: 12px; text-decoration: none; border-radius: 8px; font-weight: bold;">プロに無料相談</a>
            </div>
        </article>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="google-site-verification" content="qDKunZB9hZN753KuLftIbJUXeWBi3bA-HfSS-gej1KA" />
        <title>AI補助金ナビ 2026</title>
    </head>
    <body style="max-width: 600px; margin: 0 auto; background: #f1f3f4; padding: 20px; font-family: sans-serif;">
        <header style="text-align: center; padding: 20px 0;">
            <h1 style="color: #202124; font-size: 1.6rem;">AI補助金要約ナビ</h1>
            <p style="color: #5f6368; font-size: 0.8rem;">最終更新: {now}</p>
        </header>
        <main>{list_items}</main>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def fetch_data():
    res = requests.get("https://j-net21.smrj.go.jp/snavi/articles", timeout=30)
    soup = BeautifulSoup(res.text, 'html.parser')
    articles = soup.select('h3')[:5] # AIコスト節約のため、まずは5件に限定
    return [{"title": a.get_text(strip=True), "link": "https://j-net21.smrj.go.jp" + a.find('a')['href']} for a in articles if a.find('a')]

if __name__ == "__main__":
    generate_html(fetch_data())
