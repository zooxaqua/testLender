# Yahoo News Stream アプリケーション

Yahoo NewsのRSSフィードとスクレイピングを組み合わせて、最新ニュースのヘッドラインを表示するWebアプリケーションです。

## 📋 目次

- [概要](#概要)
- [フォルダ構成](#フォルダ構成)
- [主要機能](#主要機能)
- [技術スタック](#技術スタック)
- [セットアップ](#セットアップ)
- [API仕様](#api仕様)
- [デプロイ](#デプロイ)
- [注意事項](#注意事項)

---

## 概要

このアプリケーションは、Yahoo Newsから最新のヘッドラインを取得してWebページに表示します。データソースとして以下の2つの方法をサポートしています：

1. **RSSフィード** - Yahoo NewsのRSSから記事情報を取得
2. **Webスクレイピング** - Yahoo Newsのトップページから記事リンクを抽出

取得したニュースはメモリ内にキャッシュされ、過度なアクセスを防ぎます。

---

## フォルダ構成

```
testLender/
├── backend/              # バックエンドアプリケーション
│   ├── main.py          # FastAPI アプリケーション本体
│   ├── requirements.txt # Python依存パッケージ
│   └── runtime.txt      # Pythonバージョン指定
├── frontend/             # フロントエンドファイル
│   └── index.html       # メインHTMLページ（CSS/JavaScript含む）
├── document/             # ドキュメント
│   └── README.md        # このファイル
└── render.yaml          # Renderデプロイ設定

```

### バックエンド (`backend/`)

FastAPIを使用したRESTful APIサーバー

- **main.py** - アプリケーションロジック
  - RSSフィード取得
  - Webスクレイピング
  - キャッシング機構
  - API エンドポイント定義

### フロントエンド (`frontend/`)

シングルページアプリケーション（SPA）

- **index.html** - UI、スタイリング、JavaScriptロジックを含む完全なページ

---

## 主要機能

### 1. ニュース取得

- **RSSモード**: Yahoo NewsのRSSフィードからニュースを取得
- **スクレイプモード**: Yahoo Newsトップページから記事リンクを抽出
- **ミックスモード**: 両方のソースから取得してマージ

### 2. キャッシング

- TTL（Time To Live）: 300秒（5分）
- ソース別にキャッシュを管理
- キャッシュ有効時はバックグラウンドで更新

### 3. レスポンシブUI

- カードベースのレイアウト
- ダークモードデザイン
- モバイル対応

### 4. 設定可能なオプション

- データソース選択（RSS / Scrape / Mixed）
- 表示件数制限（1〜50件）
- 手動リフレッシュ機能

---

## 技術スタック

### バックエンド

- **FastAPI** - Webフレームワーク
- **httpx** - 非同期HTTPクライアント
- **feedparser** - RSSフィード解析
- **BeautifulSoup4** - HTMLパーサー
- **Jinja2** - テンプレートエンジン
- **uvicorn** - ASGIサーバー

### フロントエンド

- **HTML5** - マークアップ
- **CSS3** - スタイリング（Googleフォント使用）
- **Vanilla JavaScript** - ロジック（フレームワーク不使用）

---

## セットアップ

### 前提条件

- Python 3.11以上

### ローカル実行手順

1. **仮想環境の作成と有効化**

```bash
python -m venv .venv
source .venv/bin/activate  # Windowsの場合: .venv\Scripts\activate
```

2. **依存パッケージのインストール**

```bash
cd backend
pip install -r requirements.txt
```

3. **アプリケーションの起動**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

または、プロジェクトルートから：

```bash
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000
```

4. **ブラウザでアクセス**

```
http://localhost:8000
```

---

## API仕様

### エンドポイント一覧

#### `GET /`

メインのHTMLページを返します。

**レスポンス**: HTML

---

#### `GET /api/news`

ニュースの一覧をJSON形式で返します。

**クエリパラメータ**:

| パラメータ | 型     | デフォルト | 説明                           |
|---------|--------|---------|-------------------------------|
| source  | string | mixed   | `rss`, `scrape`, `mixed`のいずれか |
| limit   | int    | 10      | 取得件数（1〜50）                  |

**レスポンス例**:

```json
[
  {
    "title": "ニュースタイトル",
    "url": "https://news.yahoo.co.jp/articles/...",
    "published_at": "Wed, 15 Feb 2026 12:00:00 +0900",
    "source": "rss"
  },
  {
    "title": "別のニュース",
    "url": "https://news.yahoo.co.jp/articles/...",
    "published_at": null,
    "source": "scrape"
  }
]
```

**使用例**:

```bash
# ミックスモードで12件取得
curl "http://localhost:8000/api/news?source=mixed&limit=12"

# RSSのみで20件取得
curl "http://localhost:8000/api/news?source=rss&limit=20"
```

---

#### `GET /health`

ヘルスチェック用エンドポイント

**レスポンス**:

```json
{
  "status": "ok"
}
```

---

## デプロイ

### Renderへのデプロイ

このアプリケーションはRenderで動作するように設計されています。

#### 方法1: render.yamlを使用（推奨）

1. Renderダッシュボードで **New** → **Blueprint** を選択
2. GitHubリポジトリを接続
3. `render.yaml`が自動検出され、設定が読み込まれます
4. **Deploy** をクリック

#### 方法2: 手動設定

1. Renderダッシュボードで **New** → **Web Service** を選択
2. GitHubリポジトリを接続
3. 以下の設定を入力：

| 項目              | 値                                               |
|-------------------|--------------------------------------------------|
| Name              | testlender（任意）                               |
| Environment       | Python                                           |
| Root Directory    | `backend`                                        |
| Build Command     | `pip install -r requirements.txt`                |
| Start Command     | `uvicorn main:app --host 0.0.0.0 --port $PORT`   |
| Plan              | Free（または任意のプラン）                        |

4. **Create Web Service** をクリック

#### デプロイ後の確認

デプロイが完了すると、RenderからURLが発行されます。

```
https://your-app-name.onrender.com
```

ブラウザでアクセスして動作を確認してください。

---

## 注意事項

### 利用規約

- Yahoo Newsの利用規約を遵守してください
- 過度なアクセスを避けるため、キャッシュ機能を必ず有効にしてください（デフォルトで有効）

### キャッシュ設定

- キャッシュのTTLは`main.py`の`CACHE_TTL_SECONDS`で調整可能（デフォルト: 300秒）
- キャッシュはサーバー再起動時にクリアされます

### パフォーマンス

- 無料プランのRenderでは最初のリクエストに時間がかかる場合があります（コールドスタート）
- 継続的なトラフィックがない場合、サーバーがスリープ状態になることがあります

### エラーハンドリング

- ネットワークエラーやYahoo Newsのサイト変更により、データ取得に失敗する可能性があります
- フロントエンドでエラーメッセージが表示されます

---

## トラブルシューティング

### ローカルで起動しない

- Pythonバージョンを確認（3.11以上）
- 依存パッケージが正しくインストールされているか確認
- ポート8000が既に使用されていないか確認

### ニュースが表示されない

- ブラウザの開発者ツールでネットワークエラーを確認
- `/api/news`エンドポイントに直接アクセスして、JSONレスポンスを確認
- Yahoo Newsのサイト構造が変更されている可能性（スクレイピング部分の調整が必要）

### Renderでデプロイに失敗

- ビルドログを確認
- `render.yaml`の設定が正しいか確認
- `rootDirectory: backend`が設定されているか確認

---

## ライセンス

このプロジェクトは教育・テスト目的で作成されています。

---

## 更新履歴

- **2026-02-15**: フォルダ構成をフロントエンド/バックエンドに分離
