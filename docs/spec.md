## 1. コアバリュー

1. **リアルタイム性**

    左でLaTeX編集すると、右に整形表示が遅延なく追従し、思考を止めない。

2. **LLM支援（構造支援）**

    LLMは数式変形を断定しない。代わりに、**定義参照・前提チェック・証明骨格**を支援し、考える速度を上げる。


---

## 2. 技術スタック

- **Frontend**：Nuxt 3（Vue 3, TypeScript）
- **Backend**：Python（FastAPI）
- **LLM**：OpenAI `gpt-4o-mini`

---

## 3. 画面仕様

### 3.1 レイアウト

- **左ペイン**：LaTeXエディタ（Monaco推奨）
- **右ペイン**：リアルタイムレンダリング（KaTeX優先）
- **サイドパネル**：
    - ファイルツリー
    - Git統合パネル
    - AIアシスタント

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



---

## 5. 構造化（外部化）機能

### 5.1 アウトライン

- ノート内ブロック一覧を表示（種類・タイトル推定・label・位置）
- クリックで該当箇所へジャンプ

### 5.2 定義台帳（Definition Ledger）

- `definition` ブロックを一覧化
- 各定義に「ジャンプ」「本文抜粋」を表示


---

## 6. LLM支援仕様（OpenAI `gpt-4o-mini`）

### 6.1 LLM機能

A) **Proof Skeleton生成**（構造支援）

- 入力：対象ブロック（lemma/theorem等）のLaTeX、必要なら周辺定義
- 出力：
    - 戦略候補（背理法、帰納法、ε-δ、コンパクト性…）
    - 必要そうな補題分解案
    - 必要仮定チェックリスト（抜けの可能性を提示）

        ※断定しない。候補として提示。

B) **チャット機能**

- 入力：ユーザーメッセージ、オプションでコンテキスト（ブロックまたは選択範囲）
- 出力：数学的な質問への回答（LaTeX形式の数式を含む）

---

## 7. ファイル管理

- ワークスペースベースのファイル管理
- `.tex` ファイルの読み込み・保存・作成・削除
- ディレクトリツリー表示
- Git統合（ステータス、コミット、差分表示）

---

## 8. API（FastAPI）

### 8.1 ファイル管理

- `GET /files/tree`：ファイルツリー取得
- `GET /files/{path}`：ファイル読み込み
- `PUT /files/{path}`：ファイル更新
- `POST /files`：ファイル作成
- `DELETE /files/{path}`：ファイル削除

### 8.2 解析

- `POST /parse`：latex_source → blocks

### 8.3 LLM支援

- `POST /assist/skeleton`：block_id → skeleton cards
- `POST /assist/chat`：message → response
- `POST /assist/chat/stream`：message → streaming response

### 8.4 Git統合

- `GET /git/status`：Git状態取得
- `POST /git/stage`：ファイルステージング
- `POST /git/commit`：コミット作成

---

## 9. フロント実装要件（Nuxt）

- 編集は必ず **ローカルで即反映**（プレビューの表示自体はフロントで完結）
- バックエンドは
    - 解析（ブロック更新）
    - LLM支援
    - ファイル管理

        のみ担当

- LLMは時間がかかるため、UIは必ず
    - 実行中表示（spinner等）
    - ストリーミング応答対応
    を備える
