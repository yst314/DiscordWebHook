import requests
from config import DISCORD_WEBHOOK_URL


def send_to_discord(text: str, username: str = "ナカヤマ") -> int:
    """Discord Webhook にメッセージを送信する共通関数。"""
    if not DISCORD_WEBHOOK_URL:
        print("Discord Webhook URLが設定されていません。送信をスキップします。")
        return -1
    if not text:
        print("送信するテキストがありません。")
        return -1

    data: dict[str, str] = {
        "username": username,
        "avatar_url": "https://nagauchi.notion.site/image/attachment%3Ab902c629-b9e6-4a80-ad6e-8e3fede730f7%3Aimage.png?table=block&id=1c2b7378-9dfa-8080-89e8-f7277514877b&spaceId=a484c95d-6c4f-4e4a-97ac-db6e1790d144&width=2000&userId=&cache=v2",
        "content": text,
    }

    try:
        print(f"Discord Webhook ({username}) に送信中...")
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        response.raise_for_status()
        print(f"Discordに送信しました。ステータスコード: {response.status_code}")
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Discord Webhookへの送信中にエラーが発生しました: {e}")
        return -1
