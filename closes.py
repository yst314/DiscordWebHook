import yfinance as yf

def get_close_price(ticker: str) -> float | None:
    """指定されたティッカーの終値を取得する汎用関数"""
    try:
        data = yf.download(ticker, period="1d")
        if data is None:
            return None
        if not data.empty:
            last_price = data["Close"].iloc[0]
            last_price = round(last_price, 2)
            return last_price
        else:
            return None
    except Exception as e:
        print(f"{ticker} データ取得エラー: {str(e)}")
        return None

def get_sp500_close() -> float | None:
    return get_close_price("^GSPC")

def get_nikkei225_close() -> float | None:
    return get_close_price("^N225")