import traceback
from config import GOOGLE_API_KEY, DISCORD_WEBHOOK_URL
from common_utils import get_calculated_date
from discord_sender import send_to_discord
from gemini_handler import (
    gemini_api_client,
    build_gemini_prompt,
    get_financial_summary_from_gemini,
)
from yfinance_handler import get_summary_from_yfinance


def main_logic() -> None:  # 関数名を変更して __main__ ブロックの処理と区別
    """メイン処理ロジック。"""
    calculated_date = get_calculated_date()
    print(f"対象日付: {calculated_date}")

    final_summary = None
    error_message_for_discord = None

    # 1. Gemini版を試行
    if (
        gemini_api_client and GOOGLE_API_KEY
    ):  # gemini_api_client は gemini_handler で初期化
        print("\n--- Gemini API版の処理を開始 ---")
        try:
            gemini_prompt = build_gemini_prompt(calculated_date)
            financial_summary_gemini = get_financial_summary_from_gemini(gemini_prompt)

            if financial_summary_gemini:
                final_summary = financial_summary_gemini
                print("Gemini APIからサマリーを取得しました。")
            else:
                error_message_for_discord = f"{calculated_date} の金融市場サマリー取得試行(Gemini API)で、有効な応答が得られませんでした。"
                print(error_message_for_discord)

        except Exception as e:
            print(f"Gemini API版の処理中にエラーが発生しました: {e}")
            tb_str = traceback.format_exc()
            error_message_for_discord = (
                f"Gemini API版の処理中にエラーが発生しました。\n"
                f"日付: {calculated_date}\n"
                f"エラータイプ: {type(e).__name__}\n"
                f"エラーメッセージ: {str(e)}\n"
                f"--- トレースバック --- \n```{tb_str}```"
            )
    else:
        if not GOOGLE_API_KEY:
            message = (
                "Google APIキーが設定されていないため、Gemini API版をスキップします。"
            )
            print(message)
            error_message_for_discord = message
        elif (
            not gemini_api_client
        ):  # Client初期化失敗時のメッセージはgemini_handler側で出力済みの想定
            message = "Geminiクライアントの初期化に失敗したため、Gemini API版をスキップします。"
            print(message)
            if (
                not error_message_for_discord
            ):  # 他でエラーメッセージが設定されていなければ設定
                error_message_for_discord = message

    # 2. Gemini版が失敗した場合、エラーメッセージを送信し、yfinance版にフォールバック
    if error_message_for_discord:
        if DISCORD_WEBHOOK_URL:
            print("\n--- エラー情報をDiscordに送信 ---")
            send_to_discord(
                f"⚠️ Gemini API処理エラー通知 ⚠️\n{error_message_for_discord}",
                username="エラー通知ナカヤマ",
            )
        else:
            print(
                "Discord Webhook URL未設定のため、Gemini APIエラー通知はスキップされました。"
            )

        print("\n--- yfinance版へのフォールバック処理を開始 ---")
        try:
            summary_yfinance = get_summary_from_yfinance()
            yfinance_full_summary = f"**{calculated_date} の金融市場サマリー (yfinance代替)**\n\n{summary_yfinance}"
            final_summary = yfinance_full_summary
            print("yfinance版からサマリーを取得しました。")
        except Exception as e_yf:
            print(f"yfinance版の処理中にエラーが発生しました: {e_yf}")
            tb_str_yf = traceback.format_exc()
            yfinance_error_message = (
                f"yfinance版のフォールバック処理中にもエラーが発生しました。\n"
                f"日付: {calculated_date}\n"
                f"エラータイプ: {type(e_yf).__name__}\n"
                f"エラーメッセージ: {str(e_yf)}\n"
                f"--- トレースバック --- \n```{tb_str_yf}```"
            )
            if DISCORD_WEBHOOK_URL:
                send_to_discord(
                    f"🛑 yfinanceフォールバック処理エラー通知 🛑\n{yfinance_error_message}",
                    username="エラー通知ナカヤマ",
                )
            else:
                print(
                    "Discord Webhook URL未設定のため、yfinanceフォールバックエラー通知はスキップされました。"
                )

            # yfinanceも失敗した場合の最終メッセージを設定
            if (
                final_summary is None
            ):  # まだfinal_summaryが設定されていなければ (Geminiが成功していたケースは除く)
                final_summary = f"{calculated_date} の金融市場サマリーは取得できませんでした (Geminiエラー、yfinanceもエラー)。"

    # 3. 最終的なサマリーをDiscordに送信
    if final_summary:
        if DISCORD_WEBHOOK_URL:
            print("\n--- 最終サマリーをDiscordに送信 ---")
            send_to_discord(final_summary, username="ナカヤマ")
        else:
            print("\n--- 最終サマリー (コンソール表示のみ) ---")
            print(final_summary)
            print(
                "Discord Webhook URL未設定のため、最終サマリーのDiscord送信はスキップされました。"
            )
    else:
        # このelseブロックは、Geminiもyfinanceもデータを返さず、かつエラーメッセージも特になかった稀なケース
        # (例: Geminiが正常にNoneを返し、error_message_for_discordも設定されなかった場合)
        no_summary_message = (
            f"{calculated_date} の金融市場サマリーは取得できませんでした。"
        )
        if not error_message_for_discord:  # まだエラーメッセージが設定されていなければ
            if DISCORD_WEBHOOK_URL:
                send_to_discord(f"ℹ️ {no_summary_message}", username="ナカヤマ")
            else:
                print(f"ℹ️ {no_summary_message} (Discord通知スキップ)")
        print(no_summary_message)  # コンソールには必ず表示


if __name__ == "__main__":
    # 起動時の環境変数チェック
    can_proceed = True
    if not DISCORD_WEBHOOK_URL and not GOOGLE_API_KEY:
        print(
            "エラー: 環境変数 'DISCORD_WEBHOOK_URL' および 'GOOGLE_API_KEY' が両方とも設定されていません。処理を中止します。"
        )
        can_proceed = False
    elif not DISCORD_WEBHOOK_URL:
        print(
            "警告: 環境変数 'DISCORD_WEBHOOK_URL' が設定されていません。Discordへの通知は行われません。"
        )
    elif not GOOGLE_API_KEY:
        # Geminiクライアントの初期化はgemini_handlerで行われるが、キーがない時点で警告
        print(
            "警告: 環境変数 'GOOGLE_API_KEY' が設定されていません。Gemini APIを利用した処理はスキップされます。"
        )

    if can_proceed:
        # 主要な環境変数チェックは各モジュールのインポート時やメインロジック開始前に行う
        # 例えば config.py が読み込まれた時点で DISCORD_WEBHOOK_URL がなければ discord_sender は機能しないなど。
        # gemini_handler.py でも GOOGLE_API_KEY がなければ gemini_api_client は None になる。
        # ここでは、致命的なケース（両方ない）のみ起動を止め、それ以外は警告に留めて処理を試みる。
        main_logic()
