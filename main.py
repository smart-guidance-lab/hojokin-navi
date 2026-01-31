import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# [物理単位の厳守]: 日本時間を基準とした更新日の取得
now = datetime.now().strftime('%Y年%m月%d日 %H:%M')

def generate_html(subsidies):
    """
    HTMLファイルを生成し、GitHub Pagesで公開可能な形式にする
    """
    # 並列関係にある項目のみを箇条書き（リスト化）
    list_items = ""
    for item in subsidies:
        list_items += f"""
        <article style="border: 1px solid #eee; padding: 20px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <h2 style="color: #2c3e50; margin-top: 0;">{item['title']}</h2>
            <p style="font-size: 0.9rem; color: #666;">
                <strong>地域:</strong> {item.get('region', '全国')} | 
                <strong>カテゴリー:</strong> {item.get('category', '経営支援')}
            </p>
            <a href="{item['link']}" target="_blank" style="display: inline-block; background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">詳細を確認する</a>
        </article>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>【最新】自治体補助金自動集約ナビ 2026</title>
        <meta name="description" content="毎日自動更新される補助金データベース。robots.txt制限なしの高速インデックス版。">
    </head>
    <body style="max-width: 800px; margin: 40px auto; padding: 0 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6;">
        <header style="border-bottom: 2px solid #007bff; margin-bottom: 30px; padding-bottom: 10px;">
            <h1 style="margin: 0; color: #333;">自治体補助金自動集約ナビ</h1>
            <p style="color: #888; font-size: 0.9rem;">最終自動更新: {now}</p>
        </header>
        <main>
            {list_items}
        </main>
        <footer style="margin-top: 50px; text-align: center; color: #aaa; font-size: 0.8rem;">
            &copy; 2026 Subsidy Checker Automation.
        </footer>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Success: index.html generated.")

def fetch_data():
    # スクレイピング実行
    url = "https://j-net21.smrj.go.jp/snavi/articles"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    articles = soup.select('h3')[:10]
    
    data = []
    for art in articles:
        link_tag = art.find('a')
        title = art.get_text(strip=True)
        link = "https://j-net21.smrj.go.jp" + link_tag['href'] if link_tag else url
        data.append({"title": title, "link": link})
    return data

if __name__ == "__main__":
    try:
        subsidies_data = fetch_data()
        generate_html(subsidies_data)
    except Exception as e:
        print(f"Error: {e}")
