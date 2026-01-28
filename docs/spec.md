## 1. コアバリュー

1. **リアルタイム性**

    左でLaTeX編集すると、右に整形表示が遅延なく追従し、思考を止めない。

2. **LLM支援（構造支援）**

    LLMは数式変形を断定しない。代わりに、**定義参照・前提チェック・証明骨格・Lean化**を支援し、考える速度を上げる。

3. **Leanによる機械的検証ループ**

    LaTeX→Lean（スケルトン）→Leanチェック→エラー→LLM修正案→再チェック、の往復を1画面で完結させ、部分的に正しさを保証する。


---

## 2. 技術スタック

- **Frontend**：Nuxt 3（Vue 3, TypeScript）
- **Backend**：Python（FastAPI）
- **LLM**：OpenAI `gpt-5-mini`（Responses API）
- **Lean実行**：Lean4 + mathlib（サンドボックス実行）

`gpt-5-mini` は GPT-5 系の小型・高速モデルとして提供される。 ([OpenAI Platform](https://platform.openai.com/docs/models/gpt-5-mini?utm_source=chatgpt.com))

---

## 3. 画面仕様

### 3.1 レイアウト

- **左ペイン**：LaTeXエディタ（Monaco推奨）
- **右ペイン**：リアルタイムレンダリング（KaTeX優先）
- **下部 or 右下**：Leanパネル
    - 生成Leanコード表示
    - チェック結果（成功/失敗、診断、ログ）
    - 修正パッチ提示／適用ボタン

### 3.2 リアルタイム更新要件

- エディタ入力 → 右プレビュー更新はデバウンス（300–800ms推奨）
- レンダリング失敗時も編集を止めない（右に非致命エラー表示）

---

## 4. LaTeX入力仕様

### 4.1 ブロック認識（必須）

以下の環境をブロックとして抽出する：

- `definition`, `lemma`, `theorem`, `proposition`, `corollary`, `proof`, `remark`, `example`

抽出条件：`\begin{X}`〜`\end{X}` の範囲。

### 4.2 ブロックID（必須）

- `\label{...}` があればそれを採用
- 無ければバックエンドが **安定ID**（例：`blk_...`）を付与（保存時に固定）

### 4.3 変数宣言（任意・推奨）

- `\vars{G : Group, a b c : G}` を許可

    （Lean生成時の型付け精度を上げる）


---

## 5. 構造化（外部化）機能

### 5.1 アウトライン

- ノート内ブロック一覧を表示（種類・タイトル推定・label・位置）
- クリックで該当箇所へジャンプ

### 5.2 定義台帳（Definition Ledger）

- `definition` ブロックを一覧化
- 各定義に「ジャンプ」「本文抜粋」を表示

### 5.3 記号台帳（Symbol Table）

- `\vars{...}` の内容を最優先で台帳化
- 無い場合はヒューリスティック抽出（`X, f, \epsilon` 等の初出）
- 記号ホバーで「初出へジャンプ」またはツールチップ表示

### 5.4 TODO一覧

- `\todo{...}` または `TODO:` を抽出し一覧化

---

## 6. LLM支援仕様（OpenAI `gpt-5-mini`）

### 6.1 使用API

- OpenAI **Responses API** を使用する（推奨インターフェース）。 ([OpenAI Platform](https://platform.openai.com/docs/api-reference/responses?utm_source=chatgpt.com))
- `model = "gpt-5-mini"` 固定。 ([OpenAI Platform](https://platform.openai.com/docs/models/gpt-5-mini?utm_source=chatgpt.com))

### 6.2 LLM機能（必須）

A) **Proof Skeleton生成**（構造支援）

- 入力：対象ブロック（lemma/theorem等）のLaTeX、必要なら周辺定義
- 出力：
    - 戦略候補（背理法、帰納法、ε-δ、コンパクト性…）
    - 必要そうな補題分解案
    - 必要仮定チェックリスト（抜けの可能性を提示）

        ※断定しない。候補として提示。


B) **LaTeX→Lean生成**

- 入力：対象ブロック（LaTeX）、`\vars{...}`、参照情報
- 出力：Leanコード（スケルトンを基本）
    - 宣言部（theorem/lemma）
    - 変数宣言（可能な範囲）
    - 証明は `by` + `sorry` で開始（自動完全証明は必須にしない）

C) **Leanエラー修正パッチ**

- 入力：Leanコード + Lean診断（エラー位置とメッセージ）
- 出力：**diff形式パッチ**（適用可能な最小変更）
    - import追加
    - 型や暗黙引数の補完
    - 名前解決・記法修正
    - 必要なら命題のLean表現の修正

---

## 7. Leanチェック仕様

### 7.1 実行

- バックエンドで Lean4 + mathlib をサンドボックス実行（Docker等）
- 制限：timeout（例 10秒）、メモリ上限を設定

### 7.2 入出力

- 入力：Leanコード（1ブロック単位）
- 出力：
    - `status`（success/failure）
    - `diagnostics`（行・列・メッセージ）
    - `logs`
    - `duration_ms`

### 7.3 テンプレート

- Leanコードはテンプレートに差し込んで検証する：
    - 先頭にimport群（LLM提案 + 既定セット）
    - namespace（固定でよい）
    - 対象コード本体

---

## 8. 永続化（DBなし）

DBは使わず、以下のどちらかで実装する（実装はどちらでもよいが、挙動は同一）：

- **ファイル保存**：`./data/{note_id}.json`（推奨）
- **メモリ保存**：プロセス内辞書（再起動で消える）

保持するデータ（最小）：

- `note_id`
- `title`
- `latex_source`
- `blocks`（解析結果：type, label, id, range, latex_fragment）
- `lean_artifacts`（block_idごとのlean_code、診断、ログ、パッチ履歴）

---

## 9. API（FastAPI）

### 9.1 ノート

- `POST /notes`：新規作成 → `note_id`
- `GET /notes/{note_id}`：取得（latex_source + 解析結果）
- `PUT /notes/{note_id}`：latex_source更新（保存→再解析）

### 9.2 解析

- `POST /parse`：latex_source → blocks/symbols/todos/renderer_errors

### 9.3 LLM支援

- `POST /assist/skeleton`：block_id → skeleton cards
- `POST /assist/lean/generate`：block_id → lean_code/imports/notes
- `POST /assist/lean/fix`：lean_code + diagnostics → patch(diff)

### 9.4 Leanチェック

- `POST /lean/check`：lean_code → status/diagnostics/logs/duration_ms

---

## 10. フロント実装要件（Nuxt）

- 編集は必ず **ローカルで即反映**（プレビューの表示自体はフロントで完結）
- バックエンドは
    - 解析（ブロック/台帳更新）
    - LLM支援
    - Leanチェック

        のみ担当

- Lean/LLMは時間がかかるため、UIは必ず
    - 実行中表示（spinner等）
    - キャンセル（任意）
    - 結果の差分適用
    を備える
