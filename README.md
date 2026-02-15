# News Aggregator

複数のニュースソース（Yahoo News, NHK News, Google News）から最新ニュースを統合して表示するWebアプリケーションです。

## 🚀 クイックスタート

```bash
# 依存パッケージのインストール
pip install -r backend/requirements.txt

# サーバー起動
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# ブラウザで開く
open http://localhost:8000
```

## ✨ 主な機能

- **マルチソース対応**: Yahoo, NHK, Googleから並行取得
- **リアルタイム検索**: タイトルでキーワード検索
- **柔軟なソート**: 日付順/ソース順で並び替え
- **レスポンシブUI**: モダンなダークテーマ
- **高速キャッシング**: 5分間のメモリキャッシュ

## 📚 ドキュメント

- [API仕様](document/API.md)
- [アーキテクチャ](document/ARCHITECTURE.md)
- [開発ガイド](document/DEVELOPMENT.md)
- [詳細README](document/README.md)

## 🧪 テスト

```bash
# テスト用パッケージのインストール
pip install -r backend/requirements-test.txt

# テスト実行
PYTHONPATH=/workspaces/testLender pytest tests/ -v

# カバレッジレポート
PYTHONPATH=/workspaces/testLender pytest tests/ --cov=backend --cov-report=html
```

**テスト結果**: ✅ 26/26 テスト成功

## 📁 プロジェクト構造

```
testLender/
├── backend/         # FastAPIバックエンド
│   ├── adapters/   # ニュースソースアダプター
│   ├── models/     # データモデル
│   ├── services/   # ビジネスロジック
│   └── main.py     # メインアプリケーション
├── frontend/        # HTML/CSS/JSフロントエンド
├── tests/           # pytest テストスイート
└── document/        # 詳細ドキュメント
```

## 🌐 API エンドポイント

```bash
# 全ソースから取得
GET /api/news?sources=all&limit=20

# キーワード検索
GET /api/news?keyword=技術&limit=10

# ソート指定
GET /api/news?sort_by=published_at&sort_order=desc

# 利用可能なソース一覧
GET /api/sources
```

## 🔧 技術スタック

- **Backend**: FastAPI, Pydantic, httpx, feedparser, BeautifulSoup4
- **Frontend**: Vanilla JS, CSS Grid
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Deployment**: Render (render.yaml)

## 📝 ライセンス

MIT License

---

**Phase 3A+D 実装完了**: UI/UX強化 + テスト・ドキュメント整備
