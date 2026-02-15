# 開発ガイド

このドキュメントは、Yahoo News Stream アプリケーションの開発に参加する開発者向けのガイドです。

## 目次

- [開発環境のセットアップ](#開発環境のセットアップ)
- [コードスタイル](#コードスタイル)
- [開発ワークフロー](#開発ワークフロー)
- [デバッグ](#デバッグ)
- [テスト](#テスト)
- [トラブルシューティング](#トラブルシューティング)
- [コントリビューション](#コントリビューション)

---

## 開発環境のセットアップ

### 必要なツール

- **Python**: 3.11以上
- **Git**: バージョン管理
- **VSCode** (推奨): エディタ
- **curl** または **httpie**: API テスト

### 初回セットアップ

#### 1. リポジトリのクローン

```bash
git clone https://github.com/zooxaqua/testLender.git
cd testLender
```

#### 2. 仮想環境の作成

```bash
# 仮想環境を作成
python -m venv .venv

# 仮想環境を有効化
# Linux/Mac:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

#### 3. 依存パッケージのインストール

```bash
cd backend
pip install -r requirements.txt
```

#### 4. 開発サーバーの起動

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

`--reload` オプションにより、コード変更時に自動的にサーバーが再起動されます。

#### 5. ブラウザで確認

```
http://localhost:8000
```

---

## コードスタイル

### Python

#### 型ヒント

必ず型ヒントを使用してください：

```python
# Good ✓
def _clamp_limit(limit: int) -> int:
    if limit < 1:
        return 1
    return min(limit, MAX_LIMIT)

# Bad ✗
def _clamp_limit(limit):
    if limit < 1:
        return 1
    return min(limit, MAX_LIMIT)
```

#### 命名規則

- **関数**: スネークケース `fetch_news`, `refresh_cache`
- **定数**: 大文字スネークケース `RSS_URL`, `CACHE_TTL_SECONDS`
- **プライベート関数**: アンダースコアプレフィックス `_fetch_rss`, `_now`
- **クラス**: パスカルケース (現在未使用)

#### インポート順序

```python
# 1. 標準ライブラリ
from __future__ import annotations
import asyncio
import time
from typing import Any

# 2. サードパーティライブラリ
import feedparser
import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI

# 3. ローカルモジュール（現在なし）
```

#### フォーマット

推奨ツール：

```bash
# インストール
pip install black isort

# 実行
black backend/main.py
isort backend/main.py
```

### HTML/CSS/JavaScript

#### インデント

- **HTML**: 2スペース
- **CSS**: 2スペース
- **JavaScript**: 2スペース

#### CSS変数

カラーやサイズは CSS変数を使用：

```css
:root {
  --bg: #0f1a1c;
  --accent: #f4a259;
}
```

---

## 開発ワークフロー

### ブランチ戦略

```
main (本番環境)
  ↑
  │ Pull Request & Review
  │
feature/xxx (機能開発)
fix/xxx (バグ修正)
```

### 開発の流れ

#### 1. ブランチの作成

```bash
# 機能開発
git checkout -b feature/add-category-filter

# バグ修正
git checkout -b fix/cache-expiration-bug
```

#### 2. 開発

コードを編集し、動作確認を行います。

```bash
# 開発サーバーを起動（自動リロード有効）
cd backend
uvicorn main:app --reload
```

#### 3. コミット

```bash
git add .
git commit -m "Add: カテゴリーフィルター機能を追加"
```

**コミットメッセージの規則**:

- `Add:` - 新機能追加
- `Fix:` - バグ修正
- `Update:` - 既存機能の更新
- `Refactor:` - リファクタリング
- `Docs:` - ドキュメント更新

#### 4. プッシュ

```bash
git push origin feature/add-category-filter
```

#### 5. プルリクエスト

GitHubでプルリクエストを作成し、レビューを依頼します。

---

## デバッグ

### ログの確認

uvicornはデフォルトで詳細なログを出力します：

```
INFO:     127.0.0.1:54321 - "GET /api/news?source=rss&limit=10" 200 OK
```

### デバッグプリント

開発中は`print()`でデバッグ可能：

```python
async def _fetch_news(source: str, limit: int):
    print(f"DEBUG: Fetching {limit} items from {source}")
    # ...
```

### インタラクティブデバッグ

#### VSCode デバッガー

`.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "cwd": "${workspaceFolder}/backend",
      "jinja": true
    }
  ]
}
```

ブレークポイントを設定してF5でデバッグ開始。

#### pdb (Python Debugger)

```python
import pdb

def _fetch_rss(limit: int):
    pdb.set_trace()  # ここで停止
    # ...
```

---

## テスト

### 手動テスト

#### APIエンドポイントのテスト

```bash
# ヘルスチェック
curl http://localhost:8000/health

# ニュース取得（デフォルト）
curl http://localhost:8000/api/news

# パラメータ指定
curl "http://localhost:8000/api/news?source=rss&limit=5"

# レスポンスを整形
curl -s http://localhost:8000/api/news | python -m json.tool
```

#### ブラウザでのテスト

1. http://localhost:8000 にアクセス
2. ソースとリミットを変更して動作確認
3. ブラウザの開発者ツールでネットワークタブを確認

### 自動テスト（推奨：未実装）

#### pytest のセットアップ

```bash
pip install pytest pytest-asyncio httpx
```

#### テストファイルの例

`backend/test_main.py`:

```python
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_get_news():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/news?source=rss&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
```

#### テスト実行

```bash
pytest backend/test_main.py -v
```

---

## トラブルシューティング

### よくある問題と解決策

#### 1. サーバーが起動しない

**エラー**: `ModuleNotFoundError: No module named 'fastapi'`

**解決策**:
```bash
# 仮想環境が有効化されているか確認
which python  # /path/to/.venv/bin/python であるべき

# 依存パッケージを再インストール
pip install -r requirements.txt
```

---

#### 2. ポートが既に使用されている

**エラー**: `Address already in use`

**解決策**:
```bash
# ポート8000を使用しているプロセスを確認
lsof -i :8000

# プロセスを終了
kill -9 <PID>

# または別のポートを使用
uvicorn main:app --port 8001
```

---

#### 3. キャッシュが更新されない

**問題**: 古いデータが表示され続ける

**解決策**:
```bash
# サーバーを再起動（キャッシュクリア）
# Ctrl+C でサーバー停止後、再起動

# またはキャッシュTTLを短縮
# main.py:
CACHE_TTL_SECONDS = 10  # 10秒に変更
```

---

#### 4. Yahoo Newsからデータが取得できない

**問題**: 空の配列が返される

**チェック項目**:

1. インターネット接続の確認
2. Yahoo Newsのサイト構造変更の可能性
3. タイムアウト設定の確認

**デバッグ**:
```python
# main.py に追加
async def _fetch_rss(limit: int):
    try:
        async with httpx.AsyncClient(...) as client:
            response = await client.get(RSS_URL)
            print(f"RSS Response Status: {response.status_code}")
            print(f"RSS Response Length: {len(response.text)}")
            response.raise_for_status()
    except Exception as e:
        print(f"RSS Fetch Error: {e}")
        raise
```

---

#### 5. フロントエンドが表示されない

**エラー**: `TemplateNotFound`

**解決策**:
```python
# main.py のテンプレートパスを確認
templates = Jinja2Templates(directory="../frontend")

# パスが正しいか確認
import os
print(os.path.abspath("../frontend"))  # 絶対パスを確認
```

---

## パフォーマンス最適化

### キャッシュのチューニング

```python
# より長いTTLでキャッシュヒット率を上げる
CACHE_TTL_SECONDS = 600  # 10分

# より多くのアイテムをキャッシュ
MAX_LIMIT = 100
```

### 並列処理の改善

```python
# RSSとスクレイピングを並列実行
async def _fetch_news(source: str, limit: int):
    if source == "mixed":
        rss_task = asyncio.create_task(_fetch_rss(limit))
        scrape_task = asyncio.create_task(_fetch_scrape(limit))
        rss_items, scrape_items = await asyncio.gather(rss_task, scrape_task)
        return _merge_items(rss_items, scrape_items, limit)
    # ...
```

### リクエストタイムアウトの調整

```python
# より短いタイムアウトでレスポンスを速くする
async with httpx.AsyncClient(timeout=5.0, ...) as client:
    # ...
```

---

## 新機能の追加例

### 例: カテゴリーフィルター機能

#### 1. バックエンドに追加

```python
@app.get("/api/news")
async def get_news(
    background_tasks: BackgroundTasks,
    source: str = "mixed",
    limit: int = 10,
    category: str = "all",  # 新しいパラメータ
):
    # カテゴリーフィルターのロジックを追加
    items = await _refresh_cache(source, limit)
    
    if category != "all":
        items = [item for item in items if category in item.get("url", "")]
    
    return JSONResponse(items[:limit])
```

#### 2. フロントエンドに追加

```html
<!-- index.html の controls セクションに追加 -->
<select id="category">
  <option value="all">All Categories</option>
  <option value="domestic">Domestic</option>
  <option value="world">World</option>
</select>
```

```javascript
// JavaScript に追加
const categoryEl = document.getElementById("category");

async function loadNews() {
  const category = categoryEl.value;
  const response = await fetch(
    `/api/news?source=${source}&limit=${limit}&category=${category}`
  );
  // ...
}

categoryEl.addEventListener("change", loadNews);
```

---

## コントリビューション

### プルリクエストのガイドライン

#### チェックリスト

- [ ] コードが正しく動作する
- [ ] 既存の機能を壊していない
- [ ] コメントが適切に記述されている
- [ ] コードスタイルが統一されている
- [ ] ドキュメントが更新されている（必要に応じて）

#### レビュー観点

1. **機能性**: 要件を満たしているか
2. **可読性**: コードが理解しやすいか
3. **パフォーマンス**: 非効率な処理がないか
4. **セキュリティ**: 脆弱性がないか
5. **テスト**: 動作確認されているか

---

## 開発のベストプラクティス

### 1. 小さく頻繁にコミット

```bash
# Good ✓
git commit -m "Add: RSS取得関数を追加"
git commit -m "Add: キャッシュ機能を追加"
git commit -m "Fix: タイムアウトエラーを修正"

# Bad ✗
git commit -m "全機能実装完了"  # 巨大な変更
```

### 2. エラーハンドリングを忘れずに

```python
# Good ✓
async def _fetch_rss(limit: int):
    try:
        async with httpx.AsyncClient(...) as client:
            response = await client.get(RSS_URL)
            response.raise_for_status()
    except httpx.HTTPError as e:
        print(f"HTTP Error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return []
```

### 3. 定数を使用する

```python
# Good ✓
RSS_URL = "https://news.yahoo.co.jp/rss/topics/top-picks.xml"
CACHE_TTL_SECONDS = 300

# Bad ✗
# ハードコーディング
response = await client.get("https://news.yahoo.co.jp/rss/...")
```

### 4. ドキュメントを更新する

コードを変更したら、必ず関連ドキュメントも更新してください：

- `document/README.md` - 概要や使い方
- `document/API.md` - APIの変更
- `document/ARCHITECTURE.md` - アーキテクチャの変更

---

## 参考資料

### 公式ドキュメント

- [FastAPI](https://fastapi.tiangolo.com/)
- [httpx](https://www.python-httpx.org/)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [feedparser](https://feedparser.readthedocs.io/)

### ツール

- [Postman](https://www.postman.com/) - API テスト
- [httpie](https://httpie.io/) - コマンドラインHTTPクライアント
- [Black](https://black.readthedocs.io/) - Pythonフォーマッター
- [isort](https://pycqa.github.io/isort/) - インポート整理

---

## 質問・サポート

開発中に問題が発生した場合：

1. このドキュメントのトラブルシューティングセクションを確認
2. GitHubのIssuesで既存の問題を検索
3. 新しいIssueを作成して質問

Happy Coding! 🚀
