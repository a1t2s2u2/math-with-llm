# math-with-llm

LaTeX数学ノートエディタ with LLM支援

## 概要

リアルタイムLaTeX編集とLLM支援による証明スケルトン生成を統合したWebアプリケーション。

## 主な機能

### コアバリュー（spec.mdより）

1. **リアルタイム性** - LaTeX編集→KaTeXプレビューが遅延なく追従
2. **LLM支援** - 証明戦略提案やチャットによる数学サポート

### 技術スタック

- **Backend**: FastAPI（Python 3.12）
  - LaTeX解析（ブロック抽出）
  - OpenAI gpt-4o-mini統合
  - ファイルベースのワークスペース管理

- **Frontend**: Nuxt 3（Vue 3, TypeScript）
  - デュアルペインエディタ（LaTeX + プレビュー）
  - Git統合パネル
  - アウトライン・ブロック管理

## セットアップ

### 必要なもの

- Docker & Docker Compose
- OpenAI APIキー

### 手順

1. **リポジトリクローン**

```bash
git clone <repository-url>
cd math-with-llm
```

2. **環境変数設定**

```bash
cp .env.example .env
# .envを編集してOPENAI_API_KEYを設定
```

3. **devcontainerの再起動（初回のみ）**

Docker-in-Dockerを有効化したので、VSCodeでdevcontainerを再ビルド：

- VSCode: `Cmd/Ctrl + Shift + P` → "Dev Containers: Rebuild Container"

4. **起動（推奨: Docker Compose）**

```bash
docker compose up --build
```

これだけで、バックエンド＋フロントエンドが同時に起動します。

5. **ブラウザでアクセス**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 手動起動（開発時）

Docker Composeを使わない場合：

**バックエンド:**
```bash
cd backend
uv sync
PYTHONPATH=/workspaces/math-with-llm/backend uv run uvicorn app.main:app --reload --host 0.0.0.0
```

**フロントエンド（別ターミナル）:**
```bash
cd frontend
npm install
npm run dev
```

## API構造

### ファイル管理

- `GET /files/tree` - ファイルツリー取得
- `GET /files/{path}` - ファイル読み込み
- `PUT /files/{path}` - ファイル更新
- `POST /files` - ファイル作成
- `DELETE /files/{path}` - ファイル削除

### 解析

- `POST /parse` - LaTeX解析（ブロック抽出）

### LLM支援

- `POST /assist/skeleton` - 証明スケルトン生成
- `POST /assist/chat` - チャット
- `POST /assist/chat/stream` - ストリーミングチャット

### Git統合

- `GET /git/status` - Git状態取得
- `POST /git/stage` - ファイルステージング
- `POST /git/commit` - コミット作成

## ディレクトリ構造

```
/workspaces/math-with-llm/
├── backend/              # FastAPI アプリケーション
│   └── app/
│       ├── api/         # APIエンドポイント
│       ├── models/      # Pydanticモデル
│       ├── services/    # ビジネスロジック
│       └── utils/       # ユーティリティ
├── frontend/            # Nuxt 3 アプリケーション
│   ├── components/      # Vueコンポーネント
│   ├── composables/     # Vue composables
│   ├── pages/           # ルーティングページ
│   ├── types/           # TypeScript型定義
│   └── utils/           # API client等
├── command/             # 開発用スクリプト
├── data/                # サンプルTeXファイル
├── docs/                # ドキュメント
└── docker-compose.yml
```

## 開発ツール

- **uv** - Pythonパッケージマネージャー
- **Ruff** - Pythonリンター・フォーマッター
- **pre-commit** - コミット前自動チェック

## ドキュメント

- [仕様書](docs/spec.md) - 詳細仕様
- [開発フロー](docs/development.md) - 開発環境セットアップ
- [Git運用ルール](docs/git.md) - ブランチ戦略、コミット規約

## ライセンス

MIT
