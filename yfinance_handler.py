def get_close_price_yfinance(ticker: str) -> float | None:
    """指定されたティッカーの終値をyfinanceで取得する関数"""
    try:
        import yfinance as yf  # 関数内インポート

        data = yf.download(ticker, period="1d", auto_adjust=False)
        if data is None or data.empty:
            print(f"yfinance: {ticker} のデータが空です。")
            return None
        last_price = data["Close"].iloc[-1]
        return round(float(last_price), 2)
    except Exception as e:
        print(f"yfinance: {ticker} データ取得エラー: {str(e)}")
        return None


def get_sp500_close_yfinance() -> float | None:
    return get_close_price_yfinance("^GSPC")


def get_nikkei225_close_yfinance() -> float | None:
    return get_close_price_yfinance("^N225")


def format_price_yfinance(label: str, price: float | None, currency_symbol: str) -> str:
    """価格情報をフォーマットするヘルパー関数 (yfinance版)"""
    if price is not None:
        return f"📈 {label} 前日終値: {currency_symbol}{price:,}\\n"
    else:
        return f"📈 {label} 前日終値: N/A\\n"


def get_summary_from_yfinance() -> str:
    """市場データをyfinanceで取得して、Discord用にテキストフォーマットする関数"""
    sp500_price: float | None = get_sp500_close_yfinance()
    nikkei_price: float | None = get_nikkei225_close_yfinance()

    message: str = "yfinanceによる代替情報:\\n"
    message += format_price_yfinance("S&P 500", sp500_price, "$")
    message += format_price_yfinance("日経平均", nikkei_price, "¥")
    return message
