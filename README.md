# math-with-llm

LaTeX数学ノートエディタ with LLM支援 + Lean4検証

## 概要

リアルタイムLaTeX編集、LLM支援による証明スケルトン生成、Lean4による機械的検証を統合したWebアプリケーション。

## 主な機能

### コアバリュー（spec.mdより）

1. **リアルタイム性** - LaTeX編集→KaTeXプレビューが遅延なく追従
2. **LLM支援** - 証明戦略提案、LaTeX→Lean変換、エラーパッチ生成
3. **Lean検証ループ** - LaTeX→Lean→チェック→修正を1画面で完結

### 技術スタック

- **Backend**: FastAPI（Python 3.12）
  - LaTeX解析（ブロック・シンボル・TODO抽出）
  - OpenAI gpt-5-mini統合
  - Lean4サンドボックス実行
  - ファイルベースJSON永続化

- **Frontend**: Nuxt 3（Vue 3, TypeScript）
  - デュアルペインエディタ（LaTeX + プレビュー）
  - Leanパネル（コード・診断・パッチ）
  - アウトライン・定義台帳・シンボルテーブル

- **Verification**: Lean4 + mathlib（Docker sandbox）

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

### ノート管理

- `POST /notes` - ノート作成
- `GET /notes/{note_id}` - ノート取得
- `PUT /notes/{note_id}` - LaTeX更新（自動解析）

### 解析

- `POST /parse` - LaTeX解析（ブロック/シンボル/TODO抽出）

### LLM支援

- `POST /assist/skeleton` - 証明スケルトン生成
- `POST /assist/lean/generate` - LaTeX→Lean変換
- `POST /assist/lean/fix` - Leanエラーパッチ生成

### Lean検証

- `POST /lean/check` - Leanコードチェック

## ディレクトリ構造

```
/workspaces/math-with-llm/
├── backend/              # FastAPI アプリケーション
│   ├── app/
│   │   ├── api/         # APIエンドポイント
│   │   ├── models/      # Pydanticモデル
│   │   ├── services/    # ビジネスロジック（parser, llm, lean, storage）
│   │   └── utils/       # ユーティリティ
│   └── tests/
├── frontend/            # Nuxt 3 アプリケーション
│   ├── components/      # Vueコンポーネント
│   ├── composables/     # Vue composables
│   ├── pages/           # ルーティングページ
│   ├── types/           # TypeScript型定義
│   └── utils/           # API client等
├── lean/                # Lean4サンドボックス
│   ├── Dockerfile
│   ├── template.lean
│   └── entrypoint.sh
├── data/                # ノートJSONストレージ
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
