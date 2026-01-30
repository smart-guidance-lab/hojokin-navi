import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

def notify_google():
    # GitHub Actionsが生成した一時的な認証ファイルを読み込む
    credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    # 権限スコープの設定
    scopes = ['https://www.googleapis.com/auth/indexing']
    
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=scopes)
    
    # Indexing API サービスの構築
    service = build('indexing', 'v1', credentials=credentials)
    
    # 送信したいURLを指定（Search Consoleに登録済みのドメインであること）
    target_url = "https://your-site.com/target-page"
    
    body = {
        'url': target_url,
        'type': 'URL_UPDATED'
    }
    
    # APIの実行
    result = service.urlNotifications().publish(body=body).execute()
    print(f"Success: {result}")

if __name__ == "__main__":
    notify_google()
