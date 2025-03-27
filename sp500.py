import requests
import datetime
import os

# Webhook URL
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

# S&P500のデータをYahoo Financeから取得
def get_sp500_close():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/^GSPC"
    params = {
        "range": "2d",
        "interval": "1d"
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, params=params, headers=headers)

    if res.status_code != 200:
        raise Exception(f"Yahoo Finance API error: {res.status_code}")

    try:
        closes = res.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        last_close = closes[-2]  # 前日終値（-1は今日）
        return round(last_close, 2)
    except Exception as e:
        print("レスポンス内容:", res.text)
        raise e
def send_to_discord(price):
    text = f"📈 S&P500 前日終値: ${price}"
    data = {
        "username": "ナカヤマ",
        "avatar_url": "https://nagauchi.notion.site/image/attachment%3Ab902c629-b9e6-4a80-ad6e-8e3fede730f7%3Aimage.png?table=block&id=1c2b7378-9dfa-8080-89e8-f7277514877b&spaceId=a484c95d-6c4f-4e4a-97ac-db6e1790d144&width=2000&userId=&cache=v2",
        "content": text
    }
    requests.post(WEBHOOK_URL, json=data)

# 実行
price = get_sp500_close()
send_to_discord(price)
