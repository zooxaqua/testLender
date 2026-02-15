# testLender
lenderとの連携テスト用

FastAPIで最小構成のこんにちは世界を表示するサンプルです。

## ローカル実行

ローカルで動かすための手順です。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

ブラウザで http://localhost:8000 を開くと、こんにちは世界が表示されます。

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
