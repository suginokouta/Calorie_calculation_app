import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage
from dotenv import load_dotenv

from gemini_handler import GeminiHandler
from process_and_compress_image import resize_image

app = Flask(__name__)
load_dotenv()

# LINE API設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# GeminiHandlerクラスのインスタンスを作成
gemini_handler = GeminiHandler()

@app.route("/", methods=['GET'])
def index():
    return """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI食事カロリー診断Bot</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
            background-color: #f7f9fa;
            color: #333;
            text-align: center;
            padding: 20px;
            box-sizing: border-box;
        }
        .card {
            background: white;
            padding: 40px 30px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            max-width: 480px;
            width: 100%;
        }
        h1 { font-size: 24px; margin-bottom: 12px; }
        .status {
            display: inline-block;
            background: #e6f7ec;
            color: #0b8a36;
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 16px;
        }
        p { font-size: 15px; line-height: 1.6; color: #666; margin: 8px 0; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🍽️ AI食事カロリー診断Bot</h1>
        <div class="status">● サーバー稼働中（スタンバイ完了）</div>
        <p>サーバーが正常に起動しました！</p>
        <p>LINE公式アカウントのトーク画面から食事の写真を送信してください。</p>
    </div>
</body>
</html>""", 200

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    # 画像のバイナリデータをLINEサーバーから取得
    message_content = line_bot_api.get_message_content(event.message.id)
    
    # 取得した画像のバイナリデータを処理してリサイズ
    processed_image = resize_image(message_content.content)

    # 画像を一時的に保存するためのファイル名を指定（メッセージIDでユニーク化）
    image_path = f"temp_image_{event.message.id}.jpg"
    processed_image_path = f"processed_image_{event.message.id}.jpg"
    
    try:
        # 元画像：取得したデータをファイルとして書き込み（保存）
        with open(image_path, "wb") as f:
            for chunk in message_content.iter_content():
                f.write(chunk)
                
        with open(processed_image_path, "wb") as f:
            processed_image.save(f, format="JPEG")

        # 画像を保存した後、GeminiHandlerを使って解析し、結果を取得
        result_text = gemini_handler.analyze_meal(processed_image_path)
        
        # 解析結果の整形
        try:
            # カンマで分割して余分な空白を削除
            menu_name, calories_str = result_text.split(",")
            menu_name = menu_name.strip()
            calories = int(calories_str.strip())
            
            reply_message = f"🍽️【AIカロリー診断】\nメニュー: {menu_name}\n推定カロリー: {calories} kcal"
                
        except Exception as e:
            # AIの返答が予期せぬ形式だった場合のエラーハンドリング
            print(f"データ処理エラー: {e}")
            reply_message = f"カロリーの読み取りに失敗しました。\nAIの推測結果: {result_text}"

        # LINEに結果を返信
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )
    finally:
        # サーバーの容量を圧迫しないよう、処理完了後に画像を削除
        if os.path.exists(image_path):
            os.remove(image_path)
        if os.path.exists(processed_image_path):
            os.remove(processed_image_path)

if __name__ == "__main__":
    app.run(port=5000)