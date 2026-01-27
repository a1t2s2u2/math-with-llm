# Development Workflow

本ドキュメントは、Momiji AI における標準的な開発フローを定義する。
本プロジェクトでは uv と Dev Container を前提とした開発を行う。

目的は以下である。

- 開発環境差分によるトラブルの排除
- 誰が作業しても同じ結果が得られる再現性の確保
- CI とローカル開発環境の乖離を防ぐこと

---

## 1. 基本方針

- ローカル環境依存の手動構築は行わない
- 開発・実行は Dev Container 内で完結させる

---

## 2. 開発環境

### 2.1 Dev Container

- 標準開発環境は VS Code の Dev Container とする
- 開発・実行はすべてコンテナ内で行う
- Python の依存管理は uv に統一し、pip は使用しない

### 2.2 初回セットアップ
1. リポジトリをクローンする
2. VS Code でプロジェクトを開く
3. Dev Containers: Reopen in Container を実行する

コンテナ起動時に以下が自動実行される:
- `uv sync`: 依存パッケージのインストール
- `uv run pre-commit install`: pre-commit の Git フック有効化

### 2.3 拡張機能

以下の開発支援ツールが自動でインストールされる

インストールされる拡張機能
- Rainbow Indent: インデントの装飾
- OpenAI Codex: コード補完・生成支援
- Claude Code: AI ペアプログラミング・コードレビュー支援

### 2.4 コード品質管理

本プロジェクトでは pre-commit を使用し、コミット前に自動でコード品質チェックを行う

#### チェック内容
- Ruff: Python のコード品質チェックとフォーマット
- 基本チェック: 末尾スペース、ファイル末尾改行、YAML/JSON/TOML 文法、秘密鍵検出など
- uv lock: `pyproject.toml` と `uv.lock` の整合性チェック
- ブランチ保護: `main` ブランチへの直接コミットを防止

#### 動作の流れ
pre-commitにより、コミット時に自動で下記が実行される
1. コードのチェック・修正を実行
2. 修正可能なエラー: 自動修正後、コミット失敗（修正内容を確認して再コミット）
3. 修正不可能なエラー: エラー表示してコミット失敗（手動修正が必要）

#### main ブランチ保護

`main` ブランチで直接コミットしようとすると、pre-commit により自動的にブロックされる

```bash
# main ブランチでコミットを試みる
git checkout main
git commit -m "test"

# 結果: エラーが表示されコミットが拒否される
# `no-commit-to-branch` hook failed
```

対処方法:
- 作業ブランチを作成してコミットする: `git checkout -b feat/your-feature`
- すべての変更は Pull Request 経由で main にマージする

---

## 3. 日々の開発フロー

日常的に行う操作は以下に集約する。

### 3.1 環境管理

```bash
# 環境の同期
uv sync

# パッケージの追加
uv add <package>
```

### 3.2 作業フロー
```bash
# 最新状態を同期
git pull

# ブランチ発行
git checkout -b feat/add-user-api

# コミット
git add <file>
git commit -m "feat: add user profile api"
git push origin feat/add-user-api

# 処理の実行
uv run python main.py
```
