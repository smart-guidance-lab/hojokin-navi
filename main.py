import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# [物理単位の厳守]: 日本時間を基準とした更新日の取得
now = datetime.now().strftime('%Y年%m月%d日 %H:%M')

def generate_html(subsidies):
    """
    HTMLファイルを生成し、Google所有権確認タグと収益化ボタンを埋め込む。
    """
    list_items = ""
    for item in subsidies:
        # 収益化導線：各記事に「専門家相談」ボタンを配置
        list_items += f"""
        <article style="border: 1px solid #eee; padding: 20px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <h2 style="color: #2c3e50; margin-top: 0; font-size: 1.2rem;">{item['title']}</h2>
            <p style="font-size: 0.9rem; color: #666;">
                <strong>地域:</strong> 全国 | <strong>カテゴリー:</strong> 経営支援
            </p>
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <a href="{item['link']}" target="_blank" style="flex: 1; text-align: center; background: #f8f9fa; color: #333; padding: 10px; text-decoration: none; border-radius: 5px; border: 1px solid #ddd; font-weight: bold; font-size: 0.9rem;">公式詳細を見る</a>
                <a href="https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform" target="_blank" style="flex: 1; text-align: center; background: #28a745; color: white; padding: 10px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 0.9rem;">専門家に無料相談</a>
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
        <title>【最新】自治体補助金自動集約ナビ 2026</title>
        <meta name="description" content="毎日自動更新される補助金データベース。robots.txt制限なしの高速インデックス版。">
    </head>
    <body style="max-width: 800px; margin: 40px auto; padding: 0 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333;">
        <header style="border-bottom: 3px solid #007bff; margin-bottom: 30px; padding-bottom: 10px;">
            <h1 style="margin: 0; font-size: 1.8rem;">自治体補助金自動集約ナビ</h1>
            <p style="color: #888; font-size: 0.9rem;">最終自動更新: {now} （毎日9時更新）</p>
        </header>
        <div style="background: #e7f3ff; border-left: 5px solid #007bff; padding: 15px; margin-bottom: 30px; font-size: 0.95rem;">
            <strong>お知らせ:</strong> 補助金の申請には期限があります。最新情報を確認し、早めの準備を推奨します。
        </div>
        <main>
            {list_items}
        </main>
        <footer style="margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; text-align: center; color: #aaa; font-size: 0.8rem;">
            &copy; 2026 Subsidy Checker Automation. <br>
            免責事項：情報の正確性については必ずリンク先の一次ソースをご確認ください。
        </footer>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Success: index.html generated with Verification Tag.")

def fetch_data():
    url = "https://j-net21.smrj.go.jp/snavi/articles"
    res = requests.get(url, timeout=30)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    articles = soup.select('h3')[:10]
    
    data = []
    for art in articles:
        link_tag = art.find('a')
        title = art.get_text(strip=True)
        link = "https://j-net21.smrj.go.jp" + link_tag['href'] if link_tag else url
        data.append({{"title": title, "link": link}})
    return data

if __name__ == "__main__":
    try:
        subsidies_data = fetch_data()
        generate_html(subsidies_data)
    except Exception as e:
        print(f"Error during processing: {{e}}")
