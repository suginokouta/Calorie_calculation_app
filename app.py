import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

# ご自身のAPIキーに置き換えてください
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

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
    
    # 画像を一時的に保存するためのファイル名を指定
    image_path = "temp_image.jpg"
    
    # 取得したデータをファイルとして書き込み（保存）
    with open(image_path, "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)
            
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="画像を受け取りました")
    )
