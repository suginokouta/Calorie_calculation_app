Markdown
readme_content = """# 📸 AI食事記録アプリ (AI-Calorie-Tracker)

LINEで食事の写真を送るだけで、AIがメニュー名とカロリーを推測し、Notionデータベースへ自動記録するLINE Botアプリケーションです。

---

## 💡 アプリケーションの概要

ダイエットや健康管理において「毎日の食事記録」は非常に重要ですが、メニューやカロリーを手動で入力する煩わしさが、継続の大きな壁となります。
本アプリは、日常的に使い慣れている**LINEに写真を1枚送信するだけ**で、AIによる画像解析・カロリー推測からNotionデータベースへの記録までを全自動化し、記録のハードルを極限まで下げることを目的に開発しました。

## ✨ 主な機能

- **📸 画像認識 & カロリー推測**
  送信された理食画像から、Google Gemini APIが「メニュー名」と「推定カロリー」を高精度で推測します。
- **📝 Notionデータベース自動記録**
  推測されたデータをNotion API経由で、あらかじめ指定したデータベースへ自動で書き込みます。
- **💬 LINE Bot連携**
  ユーザーのインターフェースとしてLINE Messaging APIを採用。使い慣れたチャットUIから簡単に記録が可能です。

## 🛠️ 技術スタック (Architecture)

| 分類 | 技術・サービス / ライブラリ | バージョン・備考 |
| :--- | :--- | :--- |
| **言語** | Python | 3.12.x |
| **Webフレームワーク** | Flask | Webhook受信用サーバー |
| **外部API** | LINE Messaging API | `line-bot-sdk` |
| | Google Gemini API | `google-generativeai` (モデル: `gemini-3.5-flash`) |
| | Notion API | `notion-client` |
| **インフラ / ツール** | Render | デプロイ環境 (予定) |
| | ngrok | ローカル開発・検証用トンネリングツール |
| **その他ライブラリ** | python-dotenv<br>Pillow (PIL) | 環境変数管理<br>画像処理 |


### 📦 ディレクトリ構成（主要ファイル）

コードの出力
README.md successfully generated.

```text
Calorie_calculation_app/
├── app.py               # Webサーバーの司令塔。LINEからのWebhookを受け取り、各ハンドラーへ処理を委譲
├── gemini_handler.py    # AI機能クラス (GeminiHandler)。画像解析とカロリー推測のロジックのみをカプセル化
├── notion_handler.py    # データベース機能クラス (NotionHandler)。Notion APIとの通信とデータ書き込みを担当
├── requirements.txt     # 依存パッケージ一覧
└── .env.example         # 環境変数のサンプル
```
