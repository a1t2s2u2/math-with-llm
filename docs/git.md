# Git Rules

本プロジェクトでは，品質の高いコードを安定してリリースするために，以下の Git ブランチ戦略を採用する
チーム全員がこのフローを遵守することで，手戻りのない効率的な開発を目指す

---

## 1. ブランチ戦略

| ブランチ名 | 用途 | 例 |
| :--- | :--- | :--- |
| `main` | Commit/Push 禁止<br>原則として、作業ブランチからの PR マージのみで更新する | - |
| `feat/*` | 新機能の追加や改善 | `feat/image-generator` |
| `fix/*` | 開発中に発見されたバグの修正 | `fix/login-error` |
| `chore/*` | 機能追加やバグ修正を伴わない作業<br>（ドキュメント、設定変更、依存更新、CI整備、コード整理など） | `chore/update-ruff` |

---

## 2. コミット規約

Conventional Commits 形式に基づき、以下の prefix を付ける

- feat: 新機能・機能改善
- fix: バグ修正
- refactor: 仕様変更なしの整理
- docs: ドキュメント
- test: テスト
- chore: その他（CI・依存更新など）

例:
- `feat: 会話 API の追加`
- `fix: 比較演算子のエラーを解消`
- `chore: uv lock の更新`

---

## 3. Pull Request & Merge

- すべての変更は Pull Request 経由で main にマージする
- マージ条件: CI がすべて成功していること

### PR に含める内容
- 変更の目的
- 何を変更したか
- テスト方法（または不要な理由）
- 影響範囲（DB / 外部API / 権限 / 設定 / デプロイ等）

### レビュー・マージ
- 原則 Squash merge を使用する
- PR タイトルはコミット規約（feat/fix/chore...）に合わせることを推奨
- マージ後はブランチを削除する（GitHub上でマージ時に自動削除を推奨）

---

## 4. Pull Request 後のフロー

PR がマージされたら、ローカル・リモート両方のブランチを削除する

```bash
# 1. mainブランチに移動して最新を取得
git checkout main
git pull

# 2. ローカルブランチを削除
git branch -d feat/document

# 3. リモートブランチを削除（GitHub上で削除済みの場合は不要）
git push origin --delete feat/document
```
