import os
from datetime import datetime, timezone, timedelta
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage
from dotenv import load_dotenv

from gemini_handler import GeminiHandler
from process_and_compress_image import resize_image

app = Flask(__name__)
# リクエストボディの最大サイズ制限（DoS対策: 10MB）
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
load_dotenv()

# LINE API設定
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

# セキュリティ・アクセス制限設定
# 1日あたりの診断上限回数（デフォルト: 10回、0以下の場合は無制限）
DAILY_LIMIT_PER_USER = int(os.getenv('DAILY_LIMIT_PER_USER', '10'))
# 許可されたLINE User ID（カンマ区切り、未指定時は全ユーザー許可）
ALLOWED_USER_IDS = [
    uid.strip() for uid in os.getenv('ALLOWED_USER_IDS', '').split(',') if uid.strip()
]

# ユーザーごとの利用回数記録（オンメモリ）: {user_id: {"date": "YYYY-MM-DD", "count": int}}
user_daily_counts = {}

def check_user_access(user_id: str):
    """
    ユーザーのアクセス権限（ホワイトリスト）および本日の利用回数を判定する。
    戻り値: (利用可能か: bool, 拒否メッセージまたは空文字: str)
    """
    # 1. ホワイトリストの検証（設定されている場合のみ）
    if ALLOWED_USER_IDS and user_id not in ALLOWED_USER_IDS:
        return False, "申し訳ありません。このBotは現在、許可されたユーザーのみ利用可能です。"

    # 2. 1日の利用回数制限の検証
    if DAILY_LIMIT_PER_USER > 0:
        jst = timezone(timedelta(hours=9))
        today_str = datetime.now(jst).strftime('%Y-%m-%d')
        
        user_record = user_daily_counts.get(user_id)
        if not user_record or user_record.get('date') != today_str:
            user_daily_counts[user_id] = {'date': today_str, 'count': 0}
        
        if user_daily_counts[user_id]['count'] >= DAILY_LIMIT_PER_USER:
            return False, f"本日の診断上限（1日{DAILY_LIMIT_PER_USER}回）に達しました。\n日付が変わりましたらまたご利用ください！"
            
    return True, ""

def record_user_usage(user_id: str):
    """
    ユーザーの利用回数を1増やし、本日の残り利用可能回数を返す。
    無制限の場合は -1 を返す。
    """
    if DAILY_LIMIT_PER_USER <= 0:
        return -1
        
    jst = timezone(timedelta(hours=9))
    today_str = datetime.now(jst).strftime('%Y-%m-%d')
    user_record = user_daily_counts.setdefault(user_id, {'date': today_str, 'count': 0})
    if user_record['date'] != today_str:
        user_record['date'] = today_str
        user_record['count'] = 0
    user_record['count'] += 1
    return max(0, DAILY_LIMIT_PER_USER - user_record['count'])

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
    # X-Line-Signature ヘッダーの存在確認（未設定の場合は KeyError を防ぎ 400 Bad Request を返す）
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        abort(400)

    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    user_id = getattr(event.source, 'user_id', None)

    # アクセス権限（ホワイトリスト）および本日の利用回数制限チェック
    if user_id:
        is_allowed, error_msg = check_user_access(user_id)
        if not is_allowed:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=error_msg)
            )
            return

    # 画像のバイナリデータをLINEサーバーから取得
    message_content = line_bot_api.get_message_content(event.message.id)
    
    # 取得した画像のバイナリデータをオンメモリで処理・リサイズ（PIL.Imageオブジェクト）
    processed_image = resize_image(message_content.content)

    # ディスクに書き込まず、メモリ上の画像オブジェクトを直接GeminiHandlerに渡して解析
    result_text = gemini_handler.analyze_meal(processed_image)
    
    # 解析結果の整形
    try:
        # カンマで分割して余分な空白を削除
        menu_name, calories_str = result_text.split(",")
        menu_name = menu_name.strip()
        calories = int(calories_str.strip())
        
        # 診断成功時に利用回数をカウントし、残り回数を取得
        remaining = record_user_usage(user_id) if user_id else -1
        limit_notice = f"\n(本日の残り診断可能回数: {remaining}回)" if remaining >= 0 else ""

        reply_message = f"🍽️【AIカロリー診断】\nメニュー: {menu_name}\n推定カロリー: {calories} kcal{limit_notice}"
            
    except Exception as e:
        # AIの返答が予期せぬ形式だった場合のエラーハンドリング
        print(f"データ処理エラー: {e}")
        reply_message = f"カロリーの読み取りに失敗しました。\nAIの推測結果: {result_text}"

    # LINEに結果を返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )

if __name__ == "__main__":
    app.run(port=5000)