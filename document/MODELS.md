# データモデルとデザインパターン

このドキュメントでは、News Aggregator アプリケーションで使用されているデータモデルとデザインパターンについて説明します。

## 目次

- [データモデル](#データモデル)
- [アダプターパターン](#アダプターパターン)
- [NewsAggregatorサービス](#newsaggregatorサービス)
- [実装例](#実装例)

---

## データモデル

### NewsItem

`NewsItem` は、ニュース記事を表現するPydantic データモデルです。

**定義場所**: `backend/models/news.py`

#### フィールド

| フィールド名 | 型 | 必須 | 説明 |
|------------|---|------|------|
| `title` | `str` | ✓ | 記事のタイトル |
| `url` | `HttpUrl` | ✓ | 記事へのURL |
| `published_at` | `Optional[datetime]` | - | 公開日時（ISO 8601形式） |
| `source` | `str` | ✓ | ソース識別子（`yahoo`, `nhk`, `google`） |
| `source_name` | `str` | ✓ | ソースの表示名（`Yahoo News`, `NHK News`, `Google News`） |
| `summary` | `Optional[str]` | - | 記事の要約 |
| `image_url` | `Optional[HttpUrl]` | - | サムネイル画像のURL（未使用） |
| `category` | `Optional[str]` | - | 記事のカテゴリー（未使用） |

#### 使用例

```python
from backend.models import NewsItem
from datetime import datetime

# NewsItemの作成
news = NewsItem(
    title="最新のテクノロジーニュース",
    url="https://news.example.com/article/123",
    published_at=datetime(2026, 2, 15, 12, 30),
    source="yahoo",
    source_name="Yahoo News",
    summary="最新のテクノロジートレンドについての記事"
)

# JSON形式へのシリアライズ
news_dict = news.model_dump()

# 日付のISO形式変換
published_iso = news.published_at.isoformat() if news.published_at else None
```

#### Pydanticの利点

- **型安全性**: フィールドの型が自動的に検証される
- **バリデーション**: URLの形式、必須フィールドの存在などを自動チェック
- **シリアライズ/デシリアライズ**: JSON形式との変換が容易
- **ドキュメント生成**: FastAPIのOpenAPI仕様に自動的に統合される

---

## アダプターパターン

アダプターパターンを使用して、異なるニュースソースからのデータ取得を統一的なインターフェースで扱えるようにしています。

### NewsAdapter（基底クラス）

**定義場所**: `backend/adapters/base.py`

すべてのニュースアダプターの基底クラスです。

```python
from abc import ABC, abstractmethod
from typing import List
from backend.models import NewsItem

class NewsAdapter(ABC):
    def __init__(self, source_id: str, source_name: str):
        self.source_id = source_id
        self.source_name = source_name
    
    @abstractmethod
    async def fetch_news(self, limit: int = 10) -> List[NewsItem]:
        """ニュース記事を取得する抽象メソッド"""
        pass
```

### 具体的なアダプター実装

#### 1. YahooNewsAdapter

**定義場所**: `backend/adapters/yahoo_adapter.py`

Yahoo Newsから記事を取得します。RSSフィードとWebスクレイピングの両方をサポート。

**主要メソッド**:
- `fetch_news(limit)`: RSS + スクレイピングの両方から取得してマージ
- `fetch_rss_only(limit)`: RSSフィードのみから取得
- `fetch_scrape_only(limit)`: Webスクレイピングのみから取得
- `_fetch_rss(limit)`: RSSフィードの取得（内部メソッド）
- `_fetch_scrape(limit)`: Webスクレイピングの実行（内部メソッド）
- `_merge_items(rss, scrape, limit)`: 2つのソースをマージして重複除去

**特徴**:
- feedparser を使用したRSS解析
- BeautifulSoup4 を使用したHTML解析
- 重複URL の自動除去

#### 2. NHKNewsAdapter

**定義場所**: `backend/adapters/nhk_adapter.py`

NHK NewsのRSSフィードから記事を取得します。

**主要メソッド**:
- `fetch_news(limit)`: RSSフィードから記事を取得

**特徴**:
- 要約（summary）フィールドをサポート
- feedparser を使用

#### 3. GoogleNewsAdapter

**定義場所**: `backend/adapters/google_adapter.py`

Google NewsのRSSフィードから記事を取得します。

**主要メソッド**:
- `fetch_news(limit)`: RSSフィードから記事を取得

**特徴**:
- 日本語ニュース（`hl=ja&gl=JP&ceid=JP:ja`）に対応
- 要約（summary）フィールドをサポート

### アダプターの利点

1. **疎結合**: 各ニュースソースの実装詳細が隠蔽される
2. **拡張性**: 新しいソースの追加が容易
3. **テスト容易性**: モックアダプターを簡単に作成できる
4. **保守性**: 各ソースのロジックが独立して管理される

### 新しいアダプターの追加方法

```python
# backend/adapters/new_source_adapter.py
from backend.adapters.base import NewsAdapter
from backend.models import NewsItem
from typing import List

class NewSourceAdapter(NewsAdapter):
    def __init__(self):
        super().__init__(
            source_id="newsource",
            source_name="New Source Name"
        )
        self.api_url = "https://api.newsource.com/news"
    
    async def fetch_news(self, limit: int = 10) -> List[NewsItem]:
        # データ取得ロジックを実装
        items = []
        # ... API呼び出しやパース処理 ...
        return items
```

---

## NewsAggregatorサービス

**定義場所**: `backend/services/aggregator.py`

複数のニュースソースからデータを並行取得し、マージ、フィルタリング、ソートを行うサービスクラスです。

### 主要メソッド

#### 1. `fetch_from_sources(sources, limit_per_source)`

指定されたソースから並行してニュースを取得します。

```python
# 使用例
items = await aggregator.fetch_from_sources(
    sources=["yahoo", "nhk"],
    limit_per_source=15
)
```

**処理フロー**:
1. 各ソースに対応するアダプターを取得
2. `asyncio.gather()` で並行取得
3. エラーハンドリング（失敗したソースは空リストを返す）
4. 全結果を単一リストにフラット化

#### 2. `fetch_all_sources(limit_per_source)`

すべての利用可能なソースから取得します。

```python
# 使用例
items = await aggregator.fetch_all_sources(limit_per_source=20)
```

#### 3. `merge_and_sort(items, limit, sort_by, sort_order)`

記事をマージし、重複を除去し、ソートします。

```python
# 使用例
sorted_items = aggregator.merge_and_sort(
    items=items,
    limit=30,
    sort_by="published_at",  # または "source"
    sort_order="desc"        # または "asc"
)
```

**処理フロー**:
1. URLをキーとして重複除去
2. 指定されたフィールドでソート
3. 指定された件数まで制限

**ソートオプション**:
- `sort_by="published_at"`: 公開日時順（日付のない記事は最後）
- `sort_by="source"`: ソース識別子順
- `sort_order="desc"`: 降順（新しい順/Z→A）
- `sort_order="asc"`: 昇順（古い順/A→Z）

#### 4. `filter_by_keyword(items, keyword)`

タイトルでキーワード検索します。

```python
# 使用例
filtered_items = aggregator.filter_by_keyword(
    items=items,
    keyword="技術"
)
```

**特徴**:
- 大文字小文字を区別しない検索
- タイトルに対してのみ検索（本文は対象外）

#### 5. `fetch_and_aggregate(sources, limit, limit_per_source, sort_by, sort_order, keyword)`

上記のすべての処理を統合した高レベルAPIです。

```python
# 使用例
items = await aggregator.fetch_and_aggregate(
    sources=["yahoo", "nhk", "google"],
    limit=30,
    limit_per_source=15,
    sort_by="published_at",
    sort_order="desc",
    keyword="経済"
)
```

**処理フロー**:
1. 指定されたソースから並行取得（または全ソース）
2. キーワードでフィルタリング（指定されている場合）
3. マージと重複除去
4. ソート
5. 件数制限を適用
6. `NewsItem` オブジェクトのリストを返す

### エラーハンドリング

`_fetch_with_error_handling()` メソッドにより、個々のソースの取得失敗がアプリケーション全体に影響しないようになっています。

```python
async def _fetch_with_error_handling(
    self, adapter: NewsAdapter, limit: int
) -> List[NewsItem]:
    try:
        return await adapter.fetch_news(limit)
    except Exception as e:
        print(f"Error fetching from {adapter.source_id}: {e}")
        return []  # 空リストを返して処理を継続
```

**利点**:
- フォールトトレランス: 1つのソースが失敗しても他のソースは動作
- デグレーデション: 部分的なデータでもユーザーに提供

---

## 実装例

### 例1: main.pyでのAggregatorの使用

```python
# backend/main.py

# アダプターの初期化
yahoo_adapter = YahooNewsAdapter()
nhk_adapter = NHKNewsAdapter()
google_adapter = GoogleNewsAdapter()

# Aggregatorの初期化
aggregator = NewsAggregator(
    adapters={
        "yahoo": yahoo_adapter,
        "nhk": nhk_adapter,
        "google": google_adapter,
    }
)

# エンドポイントでの使用
@app.get("/api/news")
async def get_news(
    sources: Optional[str] = "all",
    limit: int = 20,
    sort_by: str = "published_at",
    sort_order: str = "desc",
    keyword: Optional[str] = None,
):
    source_list = sources.split(",") if sources != "all" else None
    
    items = await aggregator.fetch_and_aggregate(
        sources=source_list,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        keyword=keyword,
    )
    
    # NewsItemをdict形式に変換
    return [item.model_dump() for item in items]
```

### 例2: テストでのモックアダプター

```python
# tests/test_aggregator.py
from backend.adapters.base import NewsAdapter
from backend.models import NewsItem
from backend.services import NewsAggregator

class MockNewsAdapter(NewsAdapter):
    def __init__(self, source_id: str):
        super().__init__(source_id, f"{source_id.title()} News")
        self.mock_data = []
    
    async def fetch_news(self, limit: int = 10) -> List[NewsItem]:
        return self.mock_data[:limit]

# テスト
@pytest.mark.asyncio
async def test_aggregator():
    # モックアダプターのセットアップ
    mock1 = MockNewsAdapter("mock1")
    mock1.mock_data = [
        NewsItem(title="News 1", url="http://example.com/1", 
                 source="mock1", source_name="Mock1 News")
    ]
    
    mock2 = MockNewsAdapter("mock2")
    mock2.mock_data = [
        NewsItem(title="News 2", url="http://example.com/2",
                 source="mock2", source_name="Mock2 News")
    ]
    
    # Aggregatorの作成
    aggregator = NewsAggregator(adapters={"mock1": mock1, "mock2": mock2})
    
    # テスト実行
    items = await aggregator.fetch_and_aggregate(limit=10)
    assert len(items) == 2
```

### 例3: 新しいソースの追加

```python
# 1. 新しいアダプターを作成
# backend/adapters/reuters_adapter.py
from backend.adapters.base import NewsAdapter
from backend.models import NewsItem

class ReutersAdapter(NewsAdapter):
    def __init__(self):
        super().__init__("reuters", "Reuters News")
    
    async def fetch_news(self, limit: int = 10) -> List[NewsItem]:
        # 実装...
        pass

# 2. config.pyに設定を追加
# backend/config.py
NEWS_SOURCES = {
    # ... 既存のソース ...
    "reuters": {
        "name": "Reuters News",
        "rss_url": "https://www.reuters.com/rssfeed/news.xml",
    }
}

ENABLED_SOURCES = ["yahoo", "nhk", "google", "reuters"]

# 3. main.pyでアダプターを登録
# backend/main.py
from backend.adapters import ReutersAdapter

reuters_adapter = ReutersAdapter()

aggregator = NewsAggregator(
    adapters={
        "yahoo": yahoo_adapter,
        "nhk": nhk_adapter,
        "google": google_adapter,
        "reuters": reuters_adapter,  # 追加
    }
)
```

---

## まとめ

### デザインパターンの利点

1. **Adapter Pattern**:
   - 異なるニュースソースを統一的なインターフェースで扱える
   - 新しいソースの追加が容易
   - 各ソースの実装が独立

2. **Service Layer Pattern**:
   - ビジネスロジックをエンドポイントから分離
   - 再利用可能なサービスメソッド
   - テストが容易

3. **Pydantic Models**:
   - 型安全なデータ構造
   - 自動バリデーション
   - FastAPIとの統合

### 拡張の方向性

- **新しいソースの追加**: アダプターを実装するだけ
- **新しいフィールドの追加**: `NewsItem`モデルに追加
- **新しいフィルタリング**: `NewsAggregator`にメソッド追加
- **外部データソース**: アダプターでAPI/DB/ファイルなど様々なソースに対応可能

このアーキテクチャにより、保守性と拡張性の高いアプリケーションを実現しています。
