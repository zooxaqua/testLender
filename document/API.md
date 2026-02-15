# API仕様書

このドキュメントでは、News Aggregator アプリケーションのAPI仕様について詳細に説明します。

## ベースURL

- **ローカル環境**: `http://localhost:8000`
- **本番環境**: `https://your-app-name.onrender.com`

---

## エンドポイント

### 1. ルートエンドポイント

#### `GET /`

メインのHTMLページを配信します。

**リクエスト例**:
```bash
curl http://localhost:8000/
```

**レスポンス**:
- Content-Type: `text/html`
- ステータスコード: `200 OK`
- ボディ: HTMLドキュメント

**説明**:
- フロントエンドの`index.html`を返します
- UIからニュースの閲覧、検索、フィルタリング、ソートが可能です

---

### 2. ニュース取得API

#### `GET /api/news`

ニュースの一覧をJSON形式で返します。検索、フィルタリング、ソート機能をサポートします。

**クエリパラメータ**:

| パラメータ | 型     | 必須 | デフォルト      | 制約                | 説明                                           |
|---------|--------|------|----------------|---------------------|-----------------------------------------------|
| sources | string | No   | all            | 特定値またはカンマ区切り| `all`, `yahoo`, `nhk`, `google` または組み合わせ  |
| limit   | int    | No   | 20             | 1〜50              | 取得するニュースの最大件数                        |
| sort_by | string | No   | published_at   | `published_at`, `source` | ソートフィールド                               |
| sort_order | string | No | desc          | `asc`, `desc`       | ソート順（昇順/降順）                           |
| keyword | string | No   | -              | -                   | タイトルでフィルタリングするキーワード              |

**sourcesパラメータの詳細**:

- `all`: 全ソースから取得（Yahoo, NHK, Google）
- `yahoo`: Yahoo Newsのみ
- `nhk`: NHK Newsのみ
- `google`: Google Newsのみ
- `yahoo,nhk`: 複数ソースの組み合わせ（カンマ区切り）
- `mixed`: Yahoo混合モード（RSS + スクレイピング、レガシー）
- `rss`: Yahoo RSSのみ（レガシー）
- `scrape`: Yahooスクレイピングのみ（レガシー）

**リクエスト例**:

```bash
# デフォルト設定（全ソース、20件）
curl http://localhost:8000/api/news

# Yahoo + NHK、日付降順、30件
curl "http://localhost:8000/api/news?sources=yahoo,nhk&limit=30&sort_by=published_at&sort_order=desc"

# キーワード「技術」で検索
curl "http://localhost:8000/api/news?keyword=技術&limit=10"

# ソース順でソート
curl "http://localhost:8000/api/news?sort_by=source&sort_order=asc"

# Google Newsのみ、最古から5件
curl "http://localhost:8000/api/news?sources=google&limit=5&sort_order=asc"
```

**レスポンス**:

- Content-Type: `application/json`
- ステータスコード: `200 OK`

```json
[
  {
    "title": "ニュース記事のタイトル",
    "url": "https://news.yahoo.co.jp/articles/xxxxx",
    "published_at": "2026-02-15T12:34:56",
    "source": "yahoo",
    "source_name": "Yahoo News",
    "summary": "記事の要約文（利用可能な場合）"
  },
  {
    "title": "別のニュース記事",
    "url": "https://www3.nhk.or.jp/news/xxxxx",
    "published_at": "2026-02-15T11:20:00",
    "source": "nhk",
    "source_name": "NHK News",
    "summary": "NHKニュースの要約"
  }
]
```

**レスポンスフィールド**:

| フィールド      | 型                | 説明                                        |
|--------------|-------------------|-------------------------------------------|
| title        | string            | 記事のタイトル                                |
| url          | string            | 記事へのURL                                  |
| published_at | string \| null    | 公開日時（ISO 8601形式）                      |
| source       | string            | データソース識別子（`yahoo`, `nhk`, `google`） |
| source_name  | string            | データソースの表示名                           |
| summary      | string \| null    | 記事の要約（利用可能な場合）                    |

---

### 3. ソース一覧API

#### `GET /api/sources`

利用可能なニュースソースの一覧を返します。

**リクエスト例**:
```bash
curl http://localhost:8000/api/sources
```

**レスポンス**:

```json
{
  "sources": [
    {
      "id": "yahoo",
      "name": "Yahoo News",
      "enabled": true
    },
    {
      "id": "nhk",
      "name": "NHK News",
      "enabled": true
    },
    {
      "id": "google",
      "name": "Google News",
      "enabled": true
    }
  ],
  "default": "all"
}
```

**レスポンスフィールド**:

| フィールド | 型      | 説明                        |
|----------|---------|----------------------------|
| sources  | array   | ソース情報の配列              |
| sources[].id | string | ソース識別子            |
| sources[].name | string | ソース表示名          |
| sources[].enabled | boolean | ソースが有効かどうか |
| default  | string  | デフォルトソース              |

---

### 4. ヘルスチェックAPI

#### `GET /health`

**エラーレスポンス**:

パラメータが不正な場合でも、自動補正されて正常なレスポンスが返されます：

- `source`が不正な値の場合 → `mixed`として処理
- `limit`が1未満の場合 → `1`として処理
- `limit`が50を超える場合 → `50`として処理

---

### 3. ヘルスチェック

#### `GET /health`

サーバーの稼働状態を確認します。

**リクエスト例**:
```bash
curl http://localhost:8000/health
```

**レスポンス**:

```json
{
  "status": "ok"
}
```

- Content-Type: `application/json`
- ステータスコード: `200 OK`

**使用例**:
- デプロイ先でのヘルスチェック
- モニタリングツールからの死活監視
- ロードバランサーのヘルスチェック

---

## キャッシュの仕組み

### キャッシュキー

キャッシュは`source`パラメータごとに管理されます：
- `rss`
- `scrape`
- `mixed`

### キャッシュのTTL

- **有効期限**: 300秒（5分）
- 設定場所: `backend/main.py`の`CACHE_TTL_SECONDS`

### キャッシュの動作

1. **キャッシュが存在しない場合**:
   - データを取得してキャッシュに保存
   - レスポンスを返す

2. **キャッシュが有効期限内の場合**:
   - キャッシュされたデータをすぐに返す
   - データ取得は行わない

3. **キャッシュが期限切れだが件数が十分な場合**:
   - 古いキャッシュをすぐに返す
   - バックグラウンドでデータを更新

4. **キャッシュが期限切れで件数が不足する場合**:
   - データを取得してキャッシュを更新
   - 新しいデータを返す

---

## レート制限

現在、APIレベルでのレート制限は実装されていません。

ただし、キャッシュ機構により以下の制限があります：
- 同じ`source`への連続リクエストは5分間キャッシュから返される
- Yahoo Newsへの実際のアクセスは最短で5分に1回

---

## エラーハンドリング

### 外部APIエラー

Yahoo Newsへのアクセスに失敗した場合：

- ネットワークタイムアウト（10秒）
- HTTPエラー（4xx, 5xx）

これらのエラーは内部で処理され、クライアントには空の配列が返されます：

```json
[]
```

### アプリケーションエラー

予期しないエラーが発生した場合、FastAPIのデフォルトエラーハンドラが動作します：

```json
{
  "detail": "Internal Server Error"
}
```

---

## パフォーマンス

### レスポンスタイム

- **キャッシュヒット時**: < 10ms
- **キャッシュミス時**: 200-2000ms（Yahoo Newsのレスポンス時間に依存）

### 同時リクエスト

- FastAPIとuvicornは非同期処理をサポート
- 複数の同時リクエストを効率的に処理可能
- キャッシュロックにより、同じソースへの並行アクセスを制御

---

## セキュリティ

### CORS

現在、CORSの設定は行われていません。必要に応じて設定してください：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### User-Agent

Yahoo Newsへのリクエストには以下のUser-Agentが設定されています：

```
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
```

---

## 使用例

### JavaScript (Fetch API)

```javascript
// ニュースを取得
async function fetchNews(source = 'mixed', limit = 12) {
  const response = await fetch(`/api/news?source=${source}&limit=${limit}`);
  const news = await response.json();
  return news;
}

// 使用例
fetchNews('rss', 20)
  .then(news => console.log(news))
  .catch(error => console.error('Error:', error));
```

### Python (httpx)

```python
import httpx
import asyncio

async def get_news(source='mixed', limit=12):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            'http://localhost:8000/api/news',
            params={'source': source, 'limit': limit}
        )
        return response.json()

# 使用例
news = asyncio.run(get_news('rss', 20))
print(news)
```

### cURL

```bash
# シンプルなリクエスト
curl http://localhost:8000/api/news

# パラメータ付き
curl "http://localhost:8000/api/news?source=rss&limit=20"

# レスポンスを整形
curl -s http://localhost:8000/api/news | jq .

# ヘッダーを含めて表示
curl -i http://localhost:8000/api/news
```

---

## バージョニング

現在、APIのバージョニングは実装されていません。将来的に破壊的変更が必要な場合は、以下の形式を検討してください：

- `/v1/api/news`
- `/v2/api/news`

---

## 付録

### HTTPステータスコード

| コード | 説明                  |
|------|----------------------|
| 200  | 正常なレスポンス        |
| 404  | エンドポイントが見つからない |
| 500  | サーバーエラー          |

### タイムアウト設定

- Yahoo NewsへのHTTPリクエスト: 10秒
- uvicornのデフォルトタイムアウト: 設定なし（無制限）
