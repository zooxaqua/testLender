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
│   │   ├── __init__.py
│   │   ├── base.py      # NewsAdapter 基底クラス
│   │   ├── yahoo_adapter.py  # Yahoo News (RSS + Web Scraping)
│   │   ├── nhk_adapter.py    # NHK News (RSS)
│   │   └── google_adapter.py # Google News (RSS)
│   ├── models/          # データモデル
│   │   ├── __init__.py
│   │   └── news.py      # NewsItem Pydanticモデル
│   ├── services/        # ビジネスロジック層
│   │   ├── __init__.py
│   │   └── aggregator.py # NewsAggregator サービス
│   ├── config.py        # 設定管理（URL, タイムアウト, TTLなど）
│   ├── main.py          # FastAPI アプリケーション
│   ├── requirements.txt # 本番依存パッケージ
│   └── requirements-test.txt # テスト依存パッケージ
├── frontend/             # フロントエンドファイル
│   └── index.html       # SPA（検索・フィルター・ソート機能付き）
├── tests/                # テストコード
│   ├── conftest.py      # Pytestフィクスチャ
│   ├── test_models.py   # モデルのテスト
│   ├── test_adapters.py # アダプターのテスト
│   ├── test_aggregator.py # Aggregatorのテスト
│   └── test_api.py      # APIエンドポイントのテスト
├── document/             # ドキュメント
│   ├── README.md        # このファイル
│   ├── API.md           # API仕様書
│   ├── ARCHITECTURE.md  # アーキテクチャ説明
│   ├── DEVELOPMENT.md   # 開発ガイド
│   └── MODELS.md        # データモデルとパターン説明
├── render.yaml          # Renderデプロイ設定
├── requirements.txt     # ルート依存パッケージ
└── runtime.txt          # Pythonバージョン指定

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

# 特定ソースからの取得
GET /api/news?sources=yahoo,nhk&limit=30

# キーワード検索
GET /api/news?keyword=技術&limit=10

# ソート指定
GET /api/news?sort_by=published_at&sort_order=desc

# ソース一覧
GET /api/sources

# ヘルスチェック
GET /health
```

### API レスポンス例

```json
[
  {
    "title": "最新のテクノロジーニュース",
    "url": "https://news.yahoo.co.jp/articles/xxxxx",
    "published_at": "2026-02-15T12:34:56",
    "source": "yahoo",
    "source_name": "Yahoo News",
    "summary": "記事の要約文"
  },
  {
    "title": "NHKニュース速報",
    "url": "https://www3.nhk.or.jp/news/xxxxx",
    "published_at": "2026-02-15T11:20:00",
    "source": "nhk",
    "source_name": "NHK News",
    "summary": "NHKニュースの要約"
  }
]
```

---

## テスト

### テスト実行

```bash
# プロジェクトルートで実行
pytest

# カバレッジレポート付き
pytest --cov=backend --cov-report=html

# 特定のテストファイル
pytest tests/test_models.py

# 詳細出力
pytest -v
```

### テストカバレッジ

- **データモデル** (`test_models.py`)
  - NewsItemの生成とバリデーション
  - 必須フィールドのチェック
  - URL形式のバリデーション

- **アダプター** (`test_adapters.py`)
  - 各アダプターの初期化
  - ニュース取得機能
  - データのマージと重複除去

- **アグリゲーター** (`test_aggregator.py`)
  - 複数ソースからの並行取得
  - フィルタリングとソート
  - エラーハンドリング

- **API エンドポイント** (`test_api.py`)
  - 全エンドポイントのテスト
  - パラメータバリデーション
  - レスポンス形式の検証

---

## デプロイ

### Renderへのデプロイ

このアプリケーションはRenderで動作するように設計されています。

#### デプロイ設定

`render.yaml` ファイルに以下の設定が記述されています：

```yaml
services:
  - type: web
    name: testlender
    env: python
    plan: free
    buildCommand: pip install -r ./requirements.txt
    startCommand: python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    autoDeploy: true
```

#### デプロイ手順

**方法1: GitHub連携による自動デプロイ（推奨）**

1. Renderダッシュボードで **New** → **Blueprint** を選択
2. このGitHubリポジトリを接続
3. `render.yaml`が自動検出され、設定が読み込まれます
4. **Apply** または **Deploy** をクリック
5. 自動デプロイが開始されます

**方法2: 手動設定**

1. Renderダッシュボードで **New** → **Web Service** を選択
2. GitHubリポジトリを接続
3. 以下の設定を入力：

| 項目              | 値                                               |
|-------------------|--------------------------------------------------|
| Name              | testlender（任意）                               |
| Environment       | Python                                           |
| Build Command     | `pip install -r ./requirements.txt`              |
| Start Command     | `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |
| Plan              | Free（または任意のプラン）                        |

4. **Create Web Service** をクリック

#### デプロイ後の確認

デプロイが完了すると、RenderからURLが発行されます：

```
https://testlender.onrender.com
```

ブラウザでアクセスして動作を確認してください。

#### 自動デプロイ

`render.yaml` で `autoDeploy: true` が設定されているため、mainブランチへのプッシュで自動的に再デプロイされます。

---

## 注意事項

### 利用規約

- 各ニュースソースの利用規約を遵守してください
- 過度なアクセスを避けるため、キャッシュ機能を必ず有効にしてください（デフォルトで有効）

### キャッシュ設定

- キャッシュのTTLは`backend/config.py`の`CACHE_TTL_SECONDS`で調整可能（デフォルト: 300秒）
- キャッシュはサーバー再起動時にクリアされます
- キャッシュはメモリ内で管理されます（永続化なし）

### パフォーマンス

- 無料プランのRenderでは最初のリクエストに時間がかかる場合があります（コールドスタート）
- 継続的なトラフィックがない場合、サーバーがスリープ状態になることがあります
- 複数ソースからの並行取得により、レスポンスタイムが最適化されています

### エラーハンドリング

- 各ニュースソースへのアクセスは独立して処理されます
- 1つのソースが失敗しても、他のソースからデータを取得できます
- すべてのソースが失敗した場合は、空の配列が返されます

---

## トラブルシューティング

### ローカルで起動しない

- **Pythonバージョンを確認**: Python 3.11以上が必要です
  ```bash
  python --version
  ```
- **依存パッケージが正しくインストールされているか確認**
  ```bash
  pip install -r backend/requirements.txt
  ```
- **ポート8000が既に使用されていないか確認**
  ```bash
  lsof -i :8000  # Linux/Mac
  netstat -ano | findstr :8000  # Windows
  ```

### ニュースが表示されない

- **ブラウザの開発者ツールでネットワークエラーを確認**
  - F12キーを押して開発者ツールを開く
  - Networkタブでエラーを確認

- **APIエンドポイントに直接アクセス**
  ```bash
  curl http://localhost:8000/api/news?sources=all&limit=10
  ```

- **各ソースの状態を個別に確認**
  ```bash
  # Yahoo News
  curl http://localhost:8000/api/news?sources=yahoo&limit=5
  
  # NHK News
  curl http://localhost:8000/api/news?sources=nhk&limit=5
  
  # Google News
  curl http://localhost:8000/api/news?sources=google&limit=5
  ```

- **ニュースソースのサイト構造変更**
  - Yahoo Newsのスクレイピング部分は、サイト構造の変更により動作しなくなる可能性があります
  - その場合は`backend/adapters/yahoo_adapter.py`の更新が必要です

### Renderでデプロイに失敗

- **ビルドログを確認**
  - Renderダッシュボードの「Logs」タブで詳細を確認

- **render.yamlの設定を確認**
  - `buildCommand`と`startCommand`が正しいか確認
  - `autoDeploy`の設定を確認

- **依存パッケージの問題**
  - `requirements.txt`にすべての必要なパッケージが含まれているか確認
  - Pythonバージョンが`runtime.txt`で指定されているか確認

- **環境変数の確認**
  - `$PORT`変数がRenderから提供されるか確認

### キャッシュの問題

- **キャッシュをクリアしたい場合**
  - サーバーを再起動してください
  - キャッシュはメモリ内にあるため、再起動でクリアされます

- **キャッシュが効いていない**
  - `backend/config.py`の`CACHE_TTL_SECONDS`設定を確認
  - ログでキャッシュヒット/ミスを確認（実装されている場合）

---

## ドキュメント

このプロジェクトには、以下の詳細なドキュメントが含まれています：

- **[API.md](API.md)** - API仕様の詳細（エンドポイント、パラメータ、レスポンス形式、使用例）
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - システムアーキテクチャ、データフロー、デザインパターン
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - 開発ガイド、コーディング規約、ワークフロー
- **[MODELS.md](MODELS.md)** - データモデル、アダプターパターン、実装例

---

## 貢献

このプロジェクトへの貢献を歓迎します。

### 貢献方法

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add: 素晴らしい機能を追加'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

詳細は[DEVELOPMENT.md](DEVELOPMENT.md)を参照してください。

---

## ライセンス

このプロジェクトは教育・学習目的で作成されています。

各ニュースソースの利用規約を遵守してください：
- Yahoo News Japan
- NHK News
- Google News

---

## 連絡先

プロジェクトに関する質問や提案がある場合は、GitHubのIssuesをご利用ください。

---

## 更新履歴

### v2.0.0 (2026-02-15)
- マルチソース対応（Yahoo, NHK, Google News）
- アダプターパターンの導入
- サービス層の追加（NewsAggregator）
- 検索・フィルタリング機能の追加
- ソート機能の実装
- キャッシュシステムの改善
- テストカバレッジの拡充
- ドキュメントの充実

### v1.0.0 (初期リリース)
- Yahoo News対応（RSS + Scraping）
- 基本的なAPI実装
- シンプルなフロントエンドUI

---

## 更新履歴

- **2026-02-15**: フォルダ構成をフロントエンド/バックエンドに分離
