import yfinance as yf

def get_close_price(ticker: str) -> float | None:
    """指定されたティッカーの終値を取得する汎用関数"""
    try:
        data = yf.download(ticker, period="1d", auto_adjust=False)  # Ensure auto_adjust is explicitly set
        if data is None or data.empty:
            return None
        last_price = data["Close"].iloc[-1]  # Ensure we get the last closing price as a float
        return round(float(last_price), 2)
    except Exception as e:
        print(f"{ticker} データ取得エラー: {str(e)}")
        return None

def get_sp500_close() -> float | None:
    return get_close_price("^GSPC")

def get_nikkei225_close() -> float | None:
    return get_close_price("^N225")