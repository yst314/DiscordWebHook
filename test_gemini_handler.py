import unittest
from unittest.mock import patch, MagicMock

# テスト対象のモジュール内の特定の関数や変数をインポート
# モジュール自体をインポートして属性をパッチする方法も有効です
from gemini_handler import build_gemini_prompt, get_financial_summary_from_gemini
import gemini_handler  # gemini_handler.gemini_api_client をパッチするために必要


class TestGeminiHandler(unittest.TestCase):
    def test_build_gemini_prompt(self):
        """build_gemini_prompt関数が正しくプロンプトを生成するかテストします。"""
        date_str = "2023年10月26日"
        # gemini_handler内で config.GEMINI_PROMPT_TEMPLATE を使用するため、
        # 期待値はそのテンプレートに基づきます。
        # ここでは、日付が正しく挿入され、テンプレートの主要な部分が含まれるかを確認します。
        expected_substring_date = f"日付：{date_str}"
        expected_substring_instruction = (
            "Groundingツールを使用して最新の信頼できる情報にアクセスし"
        )
        expected_substring_news = "主要ニュースヘッドライン:"

        prompt = build_gemini_prompt(date_str)

        self.assertIn(expected_substring_date, prompt)
        self.assertIn(expected_substring_instruction, prompt)
        self.assertIn(expected_substring_news, prompt)

    @patch(
        "gemini_handler.genai.Client"
    )  # Clientの初期化自体をモックしてAPIキー依存をなくす
    def test_get_summary_success(self, mock_genai_client_constructor):
        """API呼び出しが成功し、テキストが返されるケースをテストします。"""
        # モックされたGeminiクライアントインスタンスを設定
        mock_client_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "テスト金融サマリー成功"
        mock_client_instance.models.generate_content.return_value = mock_response

        # gemini_handler.gemini_api_client がこのモックインスタンスを指すようにパッチ
        with patch.object(gemini_handler, "gemini_api_client", mock_client_instance):
            prompt = "テストプロンプト"
            result = get_financial_summary_from_gemini(prompt)

            self.assertEqual(result, "テスト金融サマリー成功")
            mock_client_instance.models.generate_content.assert_called_once()
            # 呼び出し引数の詳細なチェック (省略可能)
            # args, kwargs = mock_client_instance.models.generate_content.call_args
            # self.assertEqual(kwargs['contents'], prompt)

    @patch("gemini_handler.genai.Client")
    def test_get_summary_api_error(self, mock_genai_client_constructor):
        """API呼び出し中に例外が発生するケースをテストします。"""
        mock_client_instance = MagicMock()
        mock_client_instance.models.generate_content.side_effect = Exception(
            "API呼び出し失敗テスト"
        )

        with patch.object(gemini_handler, "gemini_api_client", mock_client_instance):
            prompt = "テストプロンプト"
            with self.assertRaisesRegex(Exception, "API呼び出し失敗テスト"):
                get_financial_summary_from_gemini(prompt)
            mock_client_instance.models.generate_content.assert_called_once()

    @patch("gemini_handler.genai.Client")
    def test_get_summary_no_text_response(self, mock_genai_client_constructor):
        """API応答にテキストが含まれないケースをテストします。"""
        mock_client_instance = MagicMock()

        # ケース1: response.text が None
        mock_response_none = MagicMock()
        mock_response_none.text = None
        mock_client_instance.models.generate_content.return_value = mock_response_none

        with patch.object(gemini_handler, "gemini_api_client", mock_client_instance):
            result_none = get_financial_summary_from_gemini("プロンプト text is None")
            self.assertIsNone(
                result_none, "response.textがNoneの場合、Noneが返されるべき"
            )

        # ケース2: response自体がNone (text属性アクセス前にチェックされるか)
        # generate_content が None を返すことは通常ない想定だが、念のため
        mock_client_instance.models.generate_content.return_value = None
        with patch.object(gemini_handler, "gemini_api_client", mock_client_instance):
            result_response_none = get_financial_summary_from_gemini(
                "プロンプト response is None"
            )
            # 現在の実装では response が None の場合、response.text で AttributeError が発生し、
            # それがキャッチされて raise される。None を返すのが望ましいなら要修正。
            # ここでは、現在の実装に合わせて例外が発生し、それが呼び出し元に伝わることを確認（またはNoneを期待するならテスト失敗）
            # get_financial_summary_from_gemini の中で response and response.text としているので、
            # response が None なら else に行き、None が返るはず。
            self.assertIsNone(
                result_response_none,
                "generate_contentがNoneを返した場合、Noneが返されるべき",
            )

    def test_get_summary_client_not_initialized(self):
        """gemini_api_clientがNoneの場合、早期にNoneが返されることをテストします。"""
        # gemini_handler.gemini_api_client を None としてパッチします
        with patch.object(gemini_handler, "gemini_api_client", None):
            prompt = "テストプロンプト"
            result = get_financial_summary_from_gemini(prompt)
            self.assertIsNone(result)
            # この場合、APIコイル (generate_content) は呼ばれないはずなので、そのチェックは不要


if __name__ == "__main__":
    unittest.main()
