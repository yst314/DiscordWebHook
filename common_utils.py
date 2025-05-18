import datetime


def get_calculated_date() -> str:
    """情報を取得したい日付（通常は前日）を計算し、YYYY年MM月DD日形式で返す関数。"""
    date_to_fetch = datetime.datetime.now()
    return date_to_fetch.strftime("%Y年%m月%d日")
