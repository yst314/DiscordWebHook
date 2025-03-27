import requests
import datetime

# Webhook URL
WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

# S&P500のデータをYahoo Financeから取得
def get_sp500_close():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/^GSPC"
    params = {
        "range": "2d",
        "interval": "1d"
    }
    res = requests.get(url, params=params).json()
    closes = res["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    last_close = closes[-2]  # 前日終値（-1は今日）
    return round(last_close, 2)

def send_to_discord(price):
    text = f"📈 S&P500 前日終値: ${price}"
    data = {
        "username": "ナカヤマ",
        "content": text
    }
    requests.post(WEBHOOK_URL, json=data)

# 実行
price = get_sp500_close()
send_to_discord(price)
