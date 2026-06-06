# Identity V Rank Match Bot

Discord上で動作する、第五人格（Identity V）の戦績管理・自動集計Botです。
ユーザーが対戦結果のスクリーンショットをDiscordに送信するだけで、**OpenCVを用いた画像認識**により対戦データを自動抽出し、データベースへ保存・集計を行います。

## 🌟 特徴 (Features)

*   **完全自動の戦績入力**: スクリーンショット（画像）をBotに送信するだけで、以下の情報を自動で読み取ります。
    *   **マップ** (Arms Factory, Sacred Heart Hospital, etc.)
    *   **ハンター** (Bloody Queen, Dream Witch, etc.)
    *   **サバイバー** (Mercenary, Seer, Priestess, etc. 最大4人まで)
    *   **勝敗** (Win, Lose, Draw)
    *   **通電の有無** (Decoded / Not Decoded)
*   **高速・高精度な画像認識**: OpenCV (`cv2.matchTemplate`) を活用。処理速度と精度を両立させるため、入力画像の不要なUI部分をあらかじめトリミングし、重要な情報が集まる領域に絞ってテンプレートマッチングを行っています。
*   **統計と集計**: データベースに保存された戦績データを元に、マップ別の勝率やサバイバー別の勝率、通電率などを瞬時に計算し、Discord上で見やすく表示します。

## 🛠 使用技術 (Tech Stack)

*   **言語**: Python 3
*   **Discord API**: discord.py
*   **画像認識**: OpenCV (`opencv-python`), NumPy
*   **データベース**: PostgreSQL (Heroku Postgres) / SQLite (ローカル開発時)
*   **デプロイ環境**: Heroku

## 🚀 仕組み・工夫した点 (Architecture & Insights)

1.  **画像認識の最適化**:
    スマートフォンのスクリーンショットにはチャット欄や背景などノイズとなる情報が多く含まれます。画像をそのまま認識させると処理が重く誤検知も増えるため、固定座標で画像をクロップ（トリミング）してからテンプレートマッチングを行うよう工夫しています。
2.  **マルチスケール対応**:
    送信される画像の解像度がユーザーの端末によって異なる場合に対応するため、0.8倍〜1.2倍の間で動的にテンプレートのスケールを変更しながらマッチングを行うロジックを組んでいます。
3.  **データベースへの非同期書き込み**:
    複数人が同時に画像を送信してもBotがフリーズしないよう、`asyncio` を用いた非同期処理でデータベースの書き込みとDiscordへの結果返信を行っています。

## 📂 ディレクトリ構成

```text
.
├── rank-match.py        # Botのメインプログラム（画像処理・DB操作・コマンド受付）
├── requirements.txt     # Herokuデプロイ用の依存ライブラリ一覧
├── Procfile             # Heroku起動コマンド
├── templates_map/       # マップ判定用のテンプレート画像群
├── templates_hunter/    # ハンター判定用のテンプレート画像群
├── templates_survivor/  # サバイバー判定用のテンプレート画像群
├── templates_decode/    # 通電状態判定用のテンプレート画像群
└── templates_result/    # 勝敗判定用のテンプレート画像群
```

## ⚙️ 実行方法 (How to Run)

### ローカル環境での起動
1. 本リポジトリをクローンします。
2. 必要なライブラリをインストールします。
   ```bash
   pip install -r requirements.txt
   ```
3. 環境変数 `DISCORD_TOKEN` にBotのトークンを設定します。
4. プログラムを実行します。
   ```bash
   python rank-match.py
   ```

