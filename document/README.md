# News Aggregator アプリケーション

複数のニュースソースから最新ニュースを取得・統合し、検索・フィルタリング・ソート機能を備えたWebアプリケーションです。

## 📋 目次

- [概要](#概要)
- [フォルダ構成](#フォルダ構成)
- [主要機能](#主要機能)
- [技術スタック](#技術スタック)
- [セットアップ](#セットアップ)
- [API仕様](#api仕様)
- [テスト](#テスト)
- [デプロイ](#デプロイ)

---

## 概要

このアプリケーションは、複数のニュースソースから最新のヘッドラインを取得して統合表示します。

### 対応ニュースソース

1. **Yahoo News** - RSSフィード + Webスクレイピング
2. **NHK News** - 公式RSSフィード
3. **Google News** - Googleニュース日本版RSS

### 主な特徴

- 複数ソースからの並行取得・統合
- リアルタイム検索機能
- 柔軟なソート機能（日付順/ソース順）
- 重複記事の自動除去
- レスポンシブUI
- メモリキャッシュによる高速化

---

## フォルダ構成

```
testLender/
├── backend/              # バックエンドアプリケーション
│   ├── adapters/        # ニュースソースアダプター
│   │   ├── base.py     # 基底アダプタークラス
│   │   ├── yahoo_adapter.py
│   │   ├── nhk_adapter.py
│   │   └── google_adapter.py
│   ├── models/          # データモデル
│   │   └── news.py     # NewsItem クラス  
│   ├── services/        # ビジネスロジック
│   │   └── aggregator.py # ニュース集約サービス
│   ├── config.py        # 設定管理
│   ├── main.py          # FastAPI アプリケーション
│   ├── requirements.txt # 本番依存パッケージ
│   └── requirements-test.txt # テスト依存パッケージ
├── frontend/             # フロントエンドファイル
│   └── index.html       # SPA（検索・フィルター機能付き）
├── tests/                # テストコード
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_adapters.py
│   ├── test_aggregator.py
│   └── test_api.py
├── document/             # ドキュメント
│   ├── README.md        # このファイル
│   ├── API.md           # API仕様書
│   ├── ARCHITECTURE.md  # アーキテクチャ
│   └── DEVELOPMENT.md   # 開発ガイド
└── render.yaml          # Renderデプロイ設定

```

---

## 主要機能

### 1. マルチソース対応

- 3つのニュースソースから並行取得
- ソース別・組み合わせでの取得が可能
- エラーハンドリング（一部失敗時も継続）

### 2. 検索・フィルタリング

- タイトルによるキーワード検索
- 大文字小文字を区別しない検索
- リアルタイム検索（入力後0.5秒でトリガー）

### 3. ソート機能

- 日付順（新しい順/古い順）
- ソース順（アルファベット順）

### 4. キャッシング

- TTL（Time To Live）: 300秒（5分）
- ソース・パラメータ別にキャッシュ管理
- バックグラウンド更新対応

### 5. レスポンシブUI

- カードベースのモダンなデザイン
- ダークモードテーマ
- モバイル対応
- ソースバッジ表示
- サマリー表示（利用可能な場合）

---

## 技術スタック

### バックエンド

- **FastAPI** - 高速Webフレームワーク
- **Pydantic** - データバリデーション
- **httpx** - 非同期HTTPクライアント
- **feedparser** - RSSフィード解析
- **BeautifulSoup4** - HTMLパーサー
- **uvicorn** - ASGIサーバー

### テスト

- **pytest** - テストフレームワーク
- **pytest-asyncio** - 非同期テストサポート
- **pytest-cov** - カバレッジ測定

### フロントエンド

- Vanilla JavaScript（フレームワークなし）
- CSS Grid レイアウト
- Fetch API

---

## セットアップ

### 必要条件

- Python 3.11以上
- pip

### インストール

```bash
# リポジトリのクローン
git clone https://github.com/zooxaqua/testLender.git
cd testLender

# 依存パッケージのインストール
pip install -r backend/requirements.txt

# テスト用パッケージのインストール（オプション）
pip install -r backend/requirements-test.txt
```

### 起動

```bash
# 開発サーバー起動
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# ブラウザで開く
open http://localhost:8000
```

---

## API仕様

詳細は[API.md](API.md)を参照してください。

### 主要エンドポイント

```bash
# ニュース取得（全ソース）
GET /api/news?sources=all&limit=20

# キーワード検索
GET /api/news?keyword=技術&limit=10

# ソート指定
GET /api/news?sort_by=published_at&sort_order=desc

# ソース一覧
GET /api/sources

# ヘルスチェック
GET /health
```

---

## テスト

### テスト実行

```bash
# 全テスト実行
pytest

# カバレッジレポート付き
pytest --cov=backend --cov-report=html

# 特定のテストファイル
pytest tests/test_models.py

# 詳細出力
pytest -v
```

### テストカバレッジ

- データモデル（NewsItem）
- アダプター（Yahoo, NHK, Google）
- アグリゲーターサービス
- APIエンドポイント

---

## デプロイ

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
