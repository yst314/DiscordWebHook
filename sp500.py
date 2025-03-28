import requests
import datetime
import os
import yfinance as yf

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

def get_sp500_close():
    ticker = "^GSPC"
    data = yf.download(ticker, period="1d")
    
    if not data.empty:
        last_price = data["Close"][ticker].iloc[0]
    else:
        raise ValueError("No data available for the specified ticker.")

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
