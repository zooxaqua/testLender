# API仕様書

このドキュメントでは、Yahoo News Stream アプリケーションのAPI仕様について詳細に説明します。

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
- UIからニュースの閲覧と設定変更が可能です

---

### 2. ニュース取得API

#### `GET /api/news`

ニュースの一覧をJSON形式で返します。

**クエリパラメータ**:

| パラメータ | 型     | 必須 | デフォルト | 制約       | 説明                                      |
|---------|--------|------|---------|-----------|------------------------------------------|
| source  | string | No   | mixed   | 特定値のみ  | `rss`, `scrape`, `mixed`のいずれか         |
| limit   | int    | No   | 10      | 1〜50     | 取得するニュースの最大件数                    |

**sourceパラメータの詳細**:

- `rss`: Yahoo NewsのRSSフィードからのみ取得
- `scrape`: Webスクレイピングでトップページから取得
- `mixed`: RSSとスクレイピングの両方から取得してマージ（デフォルト）

**リクエスト例**:

```bash
# デフォルト設定（mixed, 10件）
curl http://localhost:8000/api/news

# RSSのみ、20件
curl http://localhost:8000/api/news?source=rss&limit=20

# スクレイプのみ、12件
curl http://localhost:8000/api/news?source=scrape&limit=12

# ミックス、50件（最大）
curl http://localhost:8000/api/news?source=mixed&limit=50
```

**レスポンス**:

- Content-Type: `application/json`
- ステータスコード: `200 OK`

```json
[
  {
    "title": "ニュース記事のタイトル",
    "url": "https://news.yahoo.co.jp/articles/xxxxx",
    "published_at": "Wed, 15 Feb 2026 12:34:56 +0900",
    "source": "rss"
  },
  {
    "title": "別のニュース記事",
    "url": "https://news.yahoo.co.jp/articles/yyyyy",
    "published_at": null,
    "source": "scrape"
  }
]
```

**レスポンスフィールド**:

| フィールド      | 型                | 説明                                        |
|--------------|-------------------|-------------------------------------------|
| title        | string            | 記事のタイトル                                |
| url          | string            | 記事へのURL                                  |
| published_at | string \| null    | 公開日時（RFC 822形式、スクレイピング時はnull）     |
| source       | string            | データソース（`rss` または `scrape`）           |

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
