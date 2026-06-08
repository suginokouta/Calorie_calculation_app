import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage
from dotenv import load_dotenv

from gemini_handler import GeminiHandler
from notion_handler import NotionHandler
from process_and_compress_image import resize_image

app = Flask(__name__)
load_dotenv()

# ご自身のAPIキーに置き換えてください
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# GeminiHandlerクラスのインスタンスを作成
gemini_handler = GeminiHandler()
# NotionHandlerクラスのインスタンスを作成
notion_handler = NotionHandler()

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

    # 画像を一時的に保存するためのファイル名を指定
    image_path = "temp_image.jpg"
    processed_image_path = "processed_image.jpg"
    
    
    # 元画像：取得したデータをファイルとして書き込み（保存）
    with open(image_path, "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)
            
    with open(processed_image_path, "wb") as f:
        processed_image.save(f, format="JPEG")

    # 画像を保存した後、GeminiHandlerを使って解析し、結果を取得
    result_text = gemini_handler.analyze_meal(processed_image_path)
    
    # 解析結果をNotionに記録
    try:
        # カンマで分割して余分な空白を削除
        menu_name, calories_str = result_text.split(",")
        menu_name = menu_name.strip()
        calories = int(calories_str.strip())
        
        # NotionHandlerに書き込みを依頼
        success = notion_handler.add_record(menu_name, calories)
        
        if success:
            reply_message = f"【記録完了】\nメニュー: {menu_name}\nカロリー: {calories}kcal"
        else:
            reply_message = "Notionへの記録に失敗しました。"
            
    except Exception as e:
        # AIの返答が予期せぬ形式だった場合のエラーハンドリング
        print(f"データ処理エラー: {e}")
        reply_message = f"カロリーの読み取りに失敗しました。\nAIの推測結果: {result_text}"

    # 3. LINEに結果を返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )

if __name__ == "__main__":
    app.run(port=5000)