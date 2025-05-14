from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from config import GOOGLE_API_KEY, GEMINI_PROMPT_TEMPLATE, GEMINI_MODEL_ID

# Gemini APIのクライアントを作成
gemini_api_client = None
if GOOGLE_API_KEY:
    try:
        gemini_api_client = genai.Client(api_key=GOOGLE_API_KEY)
        print("Gemini API クライアントを作成しました。")
    except Exception as e:
        print(f"Gemini API クライアントの作成に失敗しました: {e}")
        # gemini_api_client は None のままなので、後続処理でフォールバックされる


def build_gemini_prompt(date_str: str) -> str:
    """プロンプトテンプレートに日付を埋め込む関数。"""
    return GEMINI_PROMPT_TEMPLATE.format(calculated_date=date_str)


def get_financial_summary_from_gemini(prompt: str) -> str | None:
    """Gemini API クライアントを使用して、金融市場サマリーを取得する関数。"""
    if not gemini_api_client:
        print("Geminiクライアントが初期化されていません。")
        return None
    try:
        print(f"モデル '{GEMINI_MODEL_ID}' を使用してGemini API呼び出し中...")

        google_search_tool = Tool(
            google_search=GoogleSearch()
        )  # リンターエラー箇所 (指示により無視)
        response = gemini_api_client.models.generate_content(
            model=GEMINI_MODEL_ID,
            contents=prompt,
            config=GenerateContentConfig(
                tools=[google_search_tool],
            ),
        )

        if response and response.text:
            print("Geminiからの応答を取得しました。")
            return response.text
        else:
            print("Geminiからテキスト応答がありませんでした。")
            return None

    except Exception as e:
        print(f"Gemini API呼び出し中にエラーが発生しました: {e}")
        raise  # エラーを再送出して呼び出し元でキャッチする
