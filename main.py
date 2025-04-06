import requests
import datetime
import os
from closes import get_sp500_close, get_nikkei225_close

WEBHOOK_URL: str = os.environ["DISCORD_WEBHOOK_URL"]

def format_price(label: str, price: float | None, currency_symbol: str) -> str:
    """価格情報をフォーマットするヘルパー関数"""
    if price is not None:
        return f"📈 {label} 前日終値: {currency_symbol}{price:,}\n"
    else:
        return f"📈 {label} 前日終値: なし\n"

def format_market_data() -> str:
    """市場データを取得して、Discord用にテキストフォーマットする関数"""
    today: str = datetime.datetime.now().strftime("%Y年%m月%d日")
    sp500_price: float | None = get_sp500_close()
    nikkei_price: float | None = get_nikkei225_close()
    
    message: str = f"📊 {today}の市場情報\n"
    message += format_price("S&P500", sp500_price, "$")
    message += format_price("日経平均", nikkei_price, "¥")
    
    return message

def send_to_discord(text: str) -> int:
    """Discordにメッセージを送信する関数"""
    data: dict[str, str] = {
        "username": "ナカヤマ",
        "avatar_url": "https://nagauchi.notion.site/image/attachment%3Ab902c629-b9e6-4a80-ad6e-8e3fede730f7%3Aimage.png?table=block&id=1c2b7378-9dfa-8080-89e8-f7277514877b&spaceId=a484c95d-6c4f-4e4a-97ac-db6e1790d144&width=2000&userId=&cache=v2",
        "content": text
    }
    response = requests.post(WEBHOOK_URL, json=data)
    return response.status_code

# 使用例
def main() -> None:
    message: str = format_market_data()
    status: int = send_to_discord(message)
    print(f"送信ステータス: {status}")

if __name__ == "__main__":
    main()