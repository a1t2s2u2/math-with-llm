import OpenAI from "openai";
import * as vscode from "vscode";

export interface SkeletonCard {
  strategy: string;
  description: string;
  required_lemmas: string[];
  assumptions_to_check: string[];
}

export interface LeanGeneration {
  lean_code: string;
  imports: string[];
  notes: string;
}

function getConfig() {
  const config = vscode.workspace.getConfiguration("mathWithLlm");
  const apiKey = config.get<string>("openaiApiKey", "");
  const model = config.get<string>("llmModel", "gpt-4o");
  if (!apiKey) {
    throw new Error(
      "OpenAI API key is not set. Configure mathWithLlm.openaiApiKey in settings."
    );
  }
  return { apiKey, model };
}

function createClient(): OpenAI {
  const { apiKey } = getConfig();
  return new OpenAI({ apiKey });
}

async function callLlm(
  system: string,
  prompt: string,
  jsonMode: boolean = false
): Promise<string> {
  const client = createClient();
  const { model } = getConfig();
  const response = await client.chat.completions.create({
    model,
    messages: [
      { role: "system", content: system },
      { role: "user", content: prompt },
    ],
    ...(jsonMode ? { response_format: { type: "json_object" } } : {}),
  });
  return response.choices[0].message.content || "";
}

export async function* chatStream(
  message: string,
  contextType: "block" | "selection" | null,
  contextContent: string | null
): AsyncGenerator<string> {
  let contextText = "";
  if (contextType && contextContent) {
    if (contextType === "block") {
      contextText = `\n\n参照しているブロック:\n${contextContent}`;
    } else {
      contextText = `\n\n選択されたテキスト:\n${contextContent}`;
    }
  }

  const client = createClient();
  const { model } = getConfig();
  const stream = await client.chat.completions.create({
    model,
    messages: [
      {
        role: "system",
        content:
          "あなたは数学の専門家です。" +
          "数式は必ずLaTeX形式で記述してください。" +
          "インライン数式は $...$ で囲み、" +
          "ディスプレイ数式は $$...$$ で囲んでください。" +
          "簡潔かつ正確に回答してください。",
      },
      { role: "user", content: `${message}${contextText}` },
    ],
    stream: true,
  });

  for await (const chunk of stream) {
    const delta = chunk.choices[0].delta.content;
    if (delta) {
      yield delta;
    }
  }
}

export async function generateSkeleton(
  latexFragment: string,
  context: string = ""
): Promise<SkeletonCard[]> {
  const prompt = `あなたは数学の証明アシスタントです。
以下の数学的命題を分析し、証明戦略の候補を提示してください。

命題:
${latexFragment}

コンテキスト:
${context}

2〜3個の証明戦略候補を提示してください。各戦略について:
1. 戦略名（例：「直接証明」「背理法」「数学的帰納法」）
2. アプローチの簡潔な説明
3. 必要になりそうな補題や定理
4. 確認すべき仮定や条件

以下のJSON形式で出力してください:
{
  "cards": [
    {
      "strategy": "戦略名",
      "description": "簡潔な説明",
      "required_lemmas": ["補題1", "補題2"],
      "assumptions_to_check": ["確認事項1", "確認事項2"]
    }
  ]
}

重要: 完全な証明は提供しないでください。
戦略と確認すべき点のみを提案してください。`;

  const result = JSON.parse(
    await callLlm(
      "あなたは数学の証明アシスタントです。解答ではなく戦略を提案してください。",
      prompt,
      true
    )
  );
  return (result.cards || []) as SkeletonCard[];
}

export async function generateLean(
  latexFragment: string,
  context: string = ""
): Promise<LeanGeneration> {
  const prompt = `Convert the following LaTeX mathematical statement to Lean 4 code.

Statement:
${latexFragment}

Context:
${context}

Generate Lean 4 code with:
1. Necessary imports (list them separately)
2. Type declarations for variables
3. The theorem/lemma/definition structure
4. Use 'sorry' for proof placeholders

Output as JSON:
{
  "lean_code": "theorem name : statement := by sorry",
  "imports": ["Mathlib.Algebra.Group.Defs", "..."],
  "notes": "Any important notes about the conversion"
}`;

  const result = JSON.parse(
    await callLlm(
      "You are a Lean 4 code generator. Generate skeleton code with 'sorry' placeholders.",
      prompt,
      true
    )
  );
  return result as LeanGeneration;
}
