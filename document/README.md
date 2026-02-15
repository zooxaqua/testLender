# testLender
lenderとの連携テスト用

FastAPIでYahooニュースの最新記事を取得し、フロントに表示するサンプルです。

## ローカル実行

ローカルで動かすための手順です。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

ブラウザで http://localhost:8000 を開くと、最新ニュースのカードが表示されます。

## 機能概要

- YahooニュースのRSSを取得し、スクレイピング結果と合わせて返します。
- `/api/news` でJSONを返します。
- TTL付きのメモリキャッシュで取得頻度を抑えています。

### API

`GET /api/news?source=mixed&limit=12`

- `source`: `mixed` | `rss` | `scrape`
- `limit`: 1-50

## 注意事項

- Yahooの利用規約に従って運用してください。
- スクレイピングは頻度を抑えるため、キャッシュを必ず使っています。

## Render設定

RenderのWeb Serviceに設定する内容です。

- ビルドコマンド: `pip install -r requirements.txt`
- 起動コマンド: `uvicorn main:app --host 0.0.0.0 --port $PORT`

render.yaml を使う場合は、そのままデプロイ設定として取り込めます。

## Renderへのデプロイ手順

1. Renderにログインし、New > Web Service を選びます。
2. GitHubリポジトリを連携し、このリポジトリを選択します。
3. RuntimeはPythonを選びます。
4. Build Commandに `pip install -r requirements.txt` を設定します。
5. Start Commandに `uvicorn main:app --host 0.0.0.0 --port $PORT` を設定します。
6. Create Web Serviceを押してデプロイします。

render.yaml を使う場合は、Render側でBlueprintを選ぶと設定を自動で読み込めます。
