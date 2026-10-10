
# 🍽️ AI食事カロリー診断Bot (AI Calorie Tracker)

LINEで食事の写真を送るだけで、Google Gemini AIがメニュー名と推定カロリーを瞬時に推測して返信してくれるLINE Botアプリケーションです。

---

## 📱 いますぐ体験する（ご利用方法）

本アプリはLINE公式アカウントとして稼働しています。スマートフォンから以下の手順ですぐにお試しいただけます！

> [!NOTE]
> ### ⚠️ 初回利用時のご注意（無料サーバーのスリープ仕様について）
> 本アプリは Render の無料プランで稼働しているため、約15分間アクセスがないとサーバーが自動休止（スリープ）状態に入ります。
> **スリープ中にLINEで写真を送信すると、サーバーの起動待ち（約50秒）によりLINE側の応答タイムアウトが発生し、返信が届かない場合があります。**
> 
> **【スムーズにお試しいただくための手順】**
> 1. 初回のみ、ブラウザで **デプロイ先URL（例: `https://calorie-tracker-bot-m8ld.onrender.com`）** を一度開いてください。
> 2. 「● サーバー稼働中（スタンバイ完了）」画面が表示されたらサーバーの準備完了です。
> 3. その後、LINEトーク画面から食事の写真を送信してください（すでに起動している間は数秒で即座に返信されます）。

### 1. LINE公式アカウントを友だち追加
以下のいずれかの方法でBotを友だち追加してください。

- **友だち追加リンク**: [👉 LINEで友だち追加する（@334aoghx）](https://line.me/R/ti/p/@334aoghx)
- **LINE ID検索**: `@334aoghx` で検索して追加

<div align="center">
  <p><strong>▼ 友だち追加用 QRコード ▼</strong></p>
  <a href="https://line.me/R/ti/p/@334aoghx">
    <img src="assets/line_qr.png" alt="LINE 友だち追加 QRコード" width="180">
  </a>
  <p><em>※ スマートフォンのカメラまたはLINEアプリのQRコードリーダーで読み取ってください</em></p>
</div>

---

### 2. トーク画面に食事の写真を送信
友だち追加後、トークルームを開いて記録したい料理の写真を1枚送信します。

---

### 3. AIによる診断結果をチェック！
数秒でGoogle Geminiが画像を解析し、推定メニュー名とカロリーを返信します。

```text
🍽️【AIカロリー診断】
メニュー: オムライス
推定カロリー: 700 kcal
```

---

## 💡 アプリケーションの概要

毎日の食事記録やカロリー管理は健康維持・ダイエットに欠かせませんが、毎食メニューやカロリーを手動で検索・入力するのは手間がかかり、挫折の原因になりがちです。

本アプリは、日常的に利用している**LINEに食事の写真を1枚送信するだけ**で、最新のマルチモーダルAI（Google Gemini）がメニュー名と推定カロリーを自動判定し、即座にチャットへ返信します。誰でも手軽に・ストレスフリーに食事管理を始められます。

---

## ✨ 主な機能

- **📸 簡単操作 & 画像最適化**
  LINEから送信された食事画像をEXIF情報に基づき自動回転補正し、AI解析に最適な解像度にリサイズして処理（APIトークン消費と通信量を抑制）。
- **🤖 Gemini AIによる高精度画像解析**
  Googleのマルチモーダル生成AIモデル（Gemini）を活用し、写真から料理の「メニュー名」と「推定摂取カロリー」を高精度に推測。
- **💬 LINEチャットへの即時返信**
  解析結果を分かりやすいフォーマットでLINEトーク上に自動返信。
- **🔒 セキュアな一時ファイル管理**
  サーバー上で受信・生成した画像ファイルは解析完了後に即座に自動削除され、安全かつクリーンに運用。

---

## 🛠️ 技術スタック

| カテゴリ | 技術 / サービス | 用途・備考 |
| :--- | :--- | :--- |
| **言語** | Python 3.12+ | メイン開発言語 |
| **Webフレームワーク** | Flask | LINE Webhook受信用サーバー |
| **WSGIサーバー** | Gunicorn | 本番環境用HTTPサーバー |
| **外部API** | LINE Messaging API | ユーザーインターフェース (`line-bot-sdk`) |
| | Google Gemini API | 画像解析・カロリー推測 (`google-generativeai`) |
| **画像処理** | Pillow (PIL) | 画像リサイズ、EXIF回転補正 |
| **本番インフラ** | Render (Web Service) | アプリケーションの常時稼働ホスティング |
| **開発ツール** | ngrok | ローカル検証用トンネリング |

---

## 📦 ディレクトリ構成

```text
Calorie_calculation_app/
├── assets/
│   └── line_qr.png                # LINE友だち追加用QRコード画像
├── app.py                         # メインサーバー (LINE Webhookの受信・ルーティング・返信)
├── gemini_handler.py              # Gemini API連携クラス (画像解析・プロンプト送信)
├── process_and_compress_image.py  # 画像リサイズ・EXIF補正ユーティリティ
├── Procfile                       # 本番サーバー起動設定 (gunicorn app:app)
├── requirements.txt               # 依存ライブラリ一覧
├── .env.example                   # 環境変数サンプル
└── README.md                      # プロジェクトドキュメント
```

---

## 🚀 デプロイ環境 (Render) での設定

本アプリはクラウドホスティングサービス **Render** にデプロイして稼働させることができます。

### 1. Renderの設定
- **Environment**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### 2. 環境変数 (Environment Variables)
Renderのダッシュボード（またはローカル `.env`）で以下の3項目を設定します。

| 変数名 | 説明 |
| :--- | :--- |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Developersで発行したチャネルアクセストークン（長期） |
| `LINE_CHANNEL_SECRET` | LINE Developersで発行したチャネルシークレット |
| `GEMINI_API_KEY` | Google AI Studioで発行したGemini APIキー |

### 3. LINE Developersの設定
1. デプロイ完了後、Renderから発行されたURLを確認します（例: `https://your-app-name.onrender.com`）。
2. LINE Developersコンソールの「Messaging API設定」を開きます。
3. **Webhook URL** に `https://your-app-name.onrender.com/callback` を登録します。
4. 「Webhookの利用」を **オン** に設定し、「検証」ボタンで成功することを確認します。

---

## 💻 ローカル開発環境のセットアップ

自分でカスタマイズや開発を行いたい場合の環境構築手順です。

### 1. リポジトリのクローン
```bash
git clone https://github.com/suginokouta/Calorie_calculation_app.git
cd Calorie_calculation_app
```

### 2. 仮想環境の作成と依存関係のインストール
```bash
python -m venv venv

# Windowsの場合:
venv\Scripts\activate

# Mac/Linuxの場合:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. 環境変数の設定
`.env.example` をコピーして `.env` を作成し、各APIキーを設定します。
```bash
cp .env.example .env
```

### 4. ローカルサーバー起動 & ngrokによるトンネリング
```bash
# ターミナル1: アプリ起動
python app.py

# ターミナル2: ngrokでポート5000を外部公開
ngrok http 5000
```
ngrokで払い出されたURL（`https://xxxx.ngrok-free.app/callback`）をLINE DevelopersのWebhook URLに設定して動作テストが可能です。
