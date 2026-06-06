import os
import google.generativeai as genai
import PIL.Image

class GeminiHandler:
    def __init__(self):
        # .envからGeminiのAPIキーを読み込む
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEYが設定されていません。")
        
        # APIキーをセットして初期化
        genai.configure(api_key=api_key)
        
        # Geminiのモデルを指定して初期化
        self.model = genai.GenerativeModel('gemini-3.5-flash')

    def analyze_meal(self, image_path):
        """
        保存された食事の画像を解析し、メニュー名とカロリーを推測する
        """
        try:
            # Pillowライブラリで画像を読み込む
            img = PIL.Image.open(image_path)
            
            # AIへの指示（プロンプト）
            # Notionに記録しやすいよう、シンプルな形式で出力させます
            prompt = """
            この食事の画像から、以下の2つの情報を推測してカンマ区切りで教えてください。
            余計な文章は一切含めず、「メニュー名, カロリー」の形式のみで出力してください。
            例：オムライス, 700
            """
            
            # Geminiに画像とプロンプトを送信して解析
            response = self.model.generate_content([prompt, img])
            
            # 結果を返す（例："オムライス, 700"）
            return response.text.strip()
            
        except Exception as e:
            print(f"Gemini解析エラー: {e}")
            return "解析エラー, 0"