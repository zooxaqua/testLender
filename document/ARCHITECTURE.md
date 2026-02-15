# システムアーキテクチャ

このドキュメントでは、News Aggregator アプリケーションのシステム構成とアーキテクチャについて説明します。

## 目次

- [全体構成](#全体構成)
- [アーキテクチャパターン](#アーキテクチャパターン)
- [コンポーネント構成](#コンポーネント構成)
- [データフロー](#データフロー)
- [キャッシュ戦略](#キャッシュ戦略)
- [非同期処理](#非同期処理)
- [デプロイ構成](#デプロイ構成)

---

## 全体構成

```
┌─────────────────────────────────────────────────────────────┐
│                          Browser                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Frontend (index.html)                    │   │
│  │  - HTML/CSS/JavaScript                               │   │
│  │  - News Display UI                                   │   │
│  │  - Search & Filter                                   │   │
│  │  - Auto-refresh (2 min)                              │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP/JSON
                   ↓
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                Backend (main.py)                      │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │           API Endpoints Layer                   │  │   │
│  │  │  - GET /                                       │  │   │
│  │  │  - GET /api/news                               │  │   │
│  │  │  - GET /api/sources                            │  │   │
│  │  │  - GET /health                                 │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │       Business Logic Layer (services)           │  │   │
│  │  │  - NewsAggregator Service                      │  │   │
│  │  │  - Multi-source fetching                       │  │   │
│  │  │  - Merging & Deduplication                     │  │   │
│  │  │  - Filtering & Sorting                         │  │   │
│  │  │  - Cache Management                            │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────┐  │   │
│  │  │         Data Source Layer (adapters)            │  │   │
│  │  │  - YahooNewsAdapter (RSS + Scraping)           │  │   │
│  │  │  - NHKNewsAdapter (RSS)                        │  │   │
│  │  │  - GoogleNewsAdapter (RSS)                     │  │   │
│  │  └────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────┬──────────────┬──────────────┬────────────┘
                   │              │              │
                   ↓              ↓              ↓
         ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
         │ Yahoo News  │  │  NHK News   │  │ Google News │
         │ RSS + Web   │  │     RSS     │  │     RSS     │
         └─────────────┘  └─────────────┘  └─────────────┘
```

---

## アーキテクチャパターン

### 1. レイヤードアーキテクチャ

アプリケーションは以下の3層で構成されています：

#### プレゼンテーション層
- **フロントエンド**: HTML/CSS/JavaScript
- **API**: FastAPIエンドポイント
- 責務: ユーザーインターフェース、リクエスト/レスポンス処理

#### ビジネスロジック層
- データ取得ロジック
- キャッシュ管理
- データマージング
- 責務: アプリケーションの中核機能

#### データソース層
- RSS取得
- Webスクレイピング
- 責務: 外部データソースとの連携

### 2. BFF (Backend For Frontend) パターン

バックエンドがフロントエンドのために最適化されたAPIを提供：
- 単一のエンドポイント`/api/news`でフロントエンドに必要なデータを提供
- データ形式の変換と整形
- 複数のデータソースを統合

---

## コンポーネント構成

### バックエンドコンポーネント

```
backend/
├── main.py              # FastAPIアプリケーション
│   ├── API Endpoints
│   └── Cache Management
├── config.py            # 設定管理
├── models/
│   └── news.py          # NewsItem Pydanticモデル
├── adapters/
│   ├── base.py          # NewsAdapter基底クラス
│   ├── yahoo_adapter.py # YahooNewsAdapter
│   ├── nhk_adapter.py   # NHKNewsAdapter
│   └── google_adapter.py # GoogleNewsAdapter
└── services/
    └── aggregator.py    # NewsAggregator
```

#### 主要なコンポーネントとその役割

| コンポーネント          | 責務                                |
|------------------------|-------------------------------------|
| `main.py`              | FastAPIアプリケーション本体、エンドポイント定義、キャッシュ管理 |
| `config.py`            | アプリケーション設定（URL、タイムアウト、TTLなど） |
| `models/news.py`       | NewsItemデータモデル（Pydantic） |
| `adapters/base.py`     | ニュースアダプター基底クラス |
| `adapters/yahoo_adapter.py` | Yahoo News用アダプター（RSS + Scraping） |
| `adapters/nhk_adapter.py`   | NHK News用アダプター（RSS） |
| `adapters/google_adapter.py`| Google News用アダプター（RSS） |
| `services/aggregator.py`    | 複数ソースからのニュース集約、マージ、フィルタリング |

#### API Endpoints（main.py）

| エンドポイント  | 責務                                |
|---------------|-------------------------------------|
| `GET /`       | HTMLページ配信 |
| `GET /api/news` | ニュース取得、検索、ソート、フィルタリング |
| `GET /api/sources` | 利用可能なソース一覧 |
| `GET /health` | ヘルスチェック |

#### NewsAggregator Service（services/aggregator.py）

| メソッド                | 責務                                |
|------------------------|-------------------------------------|
| `fetch_from_sources()`  | 指定されたソースから並行取得 |
| `fetch_all_sources()`   | 全ソースから並行取得 |
| `merge_and_sort()`      | 記事のマージ、重複除去、ソート |
| `filter_by_keyword()`   | キーワードでフィルタリング |
| `fetch_and_aggregate()` | 上記すべてを統合した高レベルAPI |

### フロントエンドコンポーネント

```
index.html
├── HTML Structure
│   ├── Header (Title, Description)
│   ├── Controls
│   │   ├── Search Input
│   │   ├── Source Selector
│   │   ├── Sort Controls (By/Order)
│   │   ├── Limit Selector
│   │   └── Refresh Button
│   └── Grid (News Cards)
├── CSS Styles
│   ├── Design System (CSS Variables)
│   ├── Responsive Layout
│   ├── Dark Theme
│   └── Card Animations
└── JavaScript Logic
    ├── Event Handlers (search, select, click)
    ├── API Client (fetch with parameters)
    ├── Debounced Search (500ms)
    ├── DOM Manipulation
    └── Auto-refresh (2 min interval)
    ├── Event Handlers
    ├── API Client (fetch)
    └── DOM Manipulation
```

---

## データフロー

### ニュース取得フロー

```
[User Action] → [Frontend] → [Backend API] → [Cache Check]
                                                   ↓
                                            [Cache Valid?]
                                             ↙        ↘
                                          YES         NO
                                           ↓          ↓
                                    [Return Cache] [Fetch Data]
                                                      ↓
                                              [NewsAggregator]
                                                      ↓
                                           [Parallel Fetch from Adapters]
                                            ↙        ↓        ↘
                                   [Yahoo]  [NHK]  [Google]
                                            ↘        ↓        ↙
                                              [Merge & Dedupe]
                                                      ↓
                                              [Filter & Sort]
                                                      ↓
                                              [Update Cache]
                                                      ↓
                                              [Return Data]
                                                      ↓
                    [Render UI] ← [Frontend] ← [JSON Response]
```

### 詳細なニュース取得シーケンス

```
User          Frontend        Backend          Aggregator       Adapters       News Sources
  │               │               │                │                │              │
  │  1. Search    │               │                │                │              │
  ├──────────────→│               │                │                │              │
  │               │  2. GET /api/news              │                │              │
  │               ├──────────────→│                │                │              │
  │               │               │  3. Check Cache│                │              │
  │               │               ├───────┐        │                │              │
  │               │               │←──────┘        │                │              │
  │               │               │    ↓ MISS      │                │              │
  │               │               │  4. Fetch      │                │              │
  │               │               ├───────────────→│                │              │
  │               │               │                │  5. Parallel Fetch            │
  │               │               │                ├───────────────→│              │
  │               │               │                │                ├─────────────→│
  │               │               │                │                │←─────────────┤
  │               │               │                │←───────────────┤  6. Parse    │
  │               │               │                │  7. Merge & Filter             │
  │               │               │                ├───────┐        │              │
  │               │               │                │←──────┘        │              │
  │               │               │  8. Sort       │                │              │
  │               │               │←───────────────┤                │              │
  │               │               │  9. Cache      │                │              │
  │               │               ├───────┐        │                │              │
  │               │               │←──────┘        │                │              │
  │               │  10. Response │                │                │              │
  │               │←──────────────┤                │                │              │
  │  11. Render   │               │                │                │              │
  │←──────────────┤               │                │                │              │
```
  │                    │                   ├─────────────────────→│
  │                    │                   │←─────────────────────┤
  │                    │                   │  8. Parse HTML       │
  │                    │                   ├─────────┐            │
  │                    │                   │←────────┘            │
  │                    │                   │  9. Merge & Cache    │
  │                    │                   ├─────────┐            │
  │                    │                   │←────────┘            │
  │                    │  10. JSON Response│                      │
  │                    │←──────────────────┤                      │
  │  11. Update UI     │                   │                      │
  │←───────────────────┤                   │                      │
```

---

## キャッシュ戦略

### キャッシュストラクチャ

```python
_cache = {
    "yahoo,nhk:20:published_at:desc:技術": {
        "items": [...],          # ニュース記事の配列（辞書形式）
        "fetched_at": 1708012345.67,  # UNIX timestamp
        "limit": 20              # 取得時のlimit値
    },
    "all:30:source:asc:": {
        "items": [...],
        "fetched_at": 1708012400.12,
        "limit": 30
    }
}
```

**キャッシュキー形式**: `{sources}:{limit}:{sort_by}:{sort_order}:{keyword}`
- `sources`: ソートされたソースのカンマ区切りリスト
- `limit`: 取得件数
- `sort_by`: ソート基準（`published_at` or `source`）
- `sort_order`: ソート順序（`asc` or `desc`）
- `keyword`: 検索キーワード（空文字列の場合もある）

### キャッシュポリシー

#### TTL (Time To Live)
- **デフォルト**: 300秒（5分）
- **目的**: Yahoo Newsへのアクセス頻度を抑制

#### Write-Through Strategy
- データ取得時に即座にキャッシュを更新
- 取得失敗時は古いキャッシュを保持

#### Cache Warming
- バックグラウンドタスクでキャッシュを更新
- ユーザーには古いデータを即座に返す

### キャッシュの排他制御

```python
_cache_lock = asyncio.Lock()
```

- 複数のリクエストが同時にキャッシュを更新しないように制御
- デッドロックを防ぐための非同期ロック

---

## 非同期処理

### Asyncio の活用

```python
async def _fetch_rss(limit: int):
    async with httpx.AsyncClient(...) as client:
        response = await client.get(RSS_URL)
    # ...
```

**利点**:
- I/O待機中に他のリクエストを処理可能
- スケーラビリティの向上
- リソース効率の改善

### バックグラウンドタスク

```python
@app.get("/api/news")
async def get_news(background_tasks: BackgroundTasks, ...):
    # ...
    background_tasks.add_task(_refresh_cache, source, limit)
    return JSONResponse(cached_items[:limit])
```

**利点**:
- レスポンスタイムの短縮
- ユーザー体験の向上
- 非同期キャッシュ更新

---

## デプロイ構成

### Render での構成

```
┌──────────────────────────────────────────┐
│           Render Platform                │
│  ┌────────────────────────────────────┐  │
│  │       Web Service Container        │  │
│  │  ┌──────────────────────────────┐  │  │
│  │  │     uvicorn (ASGI Server)    │  │  │
│  │  │  ┌────────────────────────┐  │  │  │
│  │  │  │  FastAPI Application   │  │  │  │
│  │  │  │  - API Endpoints       │  │  │  │
│  │  │  │  - Templates           │  │  │  │
│  │  │  └────────────────────────┘  │  │  │
│  │  └──────────────────────────────┘  │  │
│  │   Port: $PORT (Dynamic)            │  │
│  └────────────────────────────────────┘  │
│              ↓                           │
│  ┌────────────────────────────────────┐  │
│  │      HTTPS Load Balancer           │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
           ↓
    Public Internet
```

### ディレクトリマッピング

```
Repository Root
├── backend/       ← rootDirectory (Render設定)
│   ├── main.py    ← Pythonアプリケーション
│   ├── requirements.txt
│   └── runtime.txt
└── frontend/
    └── index.html ← ../frontend/ で参照
```

### 環境変数

| 変数名  | 説明                          | 提供元   |
|---------|------------------------------|---------|
| $PORT   | アプリケーションのリスニングポート | Render  |

---

## スケーラビリティ考慮事項

### 現在の制約

1. **キャッシュがメモリ内のみ**
   - 複数インスタンス間で共有されない
   - サーバー再起動でクリアされる

2. **単一サーバー構成**
   - 水平スケールアウトに制限

### 改善案

#### キャッシュの外部化
```python
# Redis を使用した例
import redis.asyncio as redis

cache = redis.Redis(host='localhost', port=6379)
```

#### セッションストア
- Redisを使用して複数インスタンス間でキャッシュを共有

#### ロードバランシング
- 複数のFastAPIインスタンスをデプロイ
- Renderの有料プランでスケーリング

---

## セキュリティ考慮事項

### 現在の実装

1. **HTTPSのみ（Render経由）**
2. **User-Agent設定** - ボット判定を回避
3. **タイムアウト設定** - DoS攻撃対策

### 追加推奨事項

1. **レート制限**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

2. **CORS設定**
   - 必要に応じて許可オリジンを制限

3. **入力検証**
   - 現在は自動補正のみ
   - より厳格なバリデーションも検討可能

---

## モニタリングとログ

### 現在の実装

- uvicornのデフォルトログ
- 標準出力への出力

### 推奨する追加項目

1. **構造化ログ**
   ```python
   import structlog
   logger = structlog.get_logger()
   ```

2. **メトリクス収集**
   - Prometheus形式でメトリクスをエクスポート
   - レスポンスタイム、エラー率などを監視

3. **エラートラッキング**
   - Sentryなどのエラートラッキングサービス

---

## 将来の拡張性

### 考えられる拡張

1. **データベース統合**
   - ニュース記事の永続化
   - 閲覧履歴の保存

2. **ユーザー認証**
   - ユーザーごとの設定保存
   - お気に入り機能

3. **通知機能**
   - WebSocketを使ったリアルタイム更新
   - プッシュ通知

4. **多言語対応**
   - 複数の言語のニュースソースをサポート

5. **データ分析**
   - トレンド分析
   - 記事の分類・タグ付け
