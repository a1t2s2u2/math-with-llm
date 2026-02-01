import * as vscode from "vscode";
import { BlockOutlineProvider } from "./blockOutline";
import { ChatPanelProvider } from "./chatPanel";
import { PreviewPanelProvider } from "./previewPanel";
import { generateSkeleton, generateLean } from "./llm";

export function activate(context: vscode.ExtensionContext) {
  const outlineProvider = new BlockOutlineProvider();
  const chatProvider = new ChatPanelProvider(context.extensionUri);
  const previewProvider = new PreviewPanelProvider(context.extensionUri);

  context.subscriptions.push(
    vscode.window.registerTreeDataProvider(
      "mathWithLlm.blockOutline",
      outlineProvider
    ),
    vscode.window.registerWebviewViewProvider(
      ChatPanelProvider.viewType,
      chatProvider
    ),
    vscode.window.registerWebviewViewProvider(
      PreviewPanelProvider.viewType,
      previewProvider
    ),

    vscode.commands.registerCommand("mathWithLlm.revealBlock", (block) => {
      outlineProvider.revealBlock(block);
    }),

    vscode.commands.registerCommand(
      "mathWithLlm.generateSkeleton",
      async () => {
        const blocks = outlineProvider.getBlocks();
        if (blocks.length === 0) {
          vscode.window.showWarningMessage("No LaTeX blocks found.");
          return;
        }

        const items = blocks.map((b) => ({
          label: `${b.type}: ${b.title || b.id}`,
          block: b,
        }));
        const picked = await vscode.window.showQuickPick(items, {
          placeHolder: "Select a block to generate skeleton for",
        });
        if (!picked) {
          return;
        }

        await vscode.window.withProgress(
          {
            location: vscode.ProgressLocation.Notification,
            title: "Generating proof skeleton...",
          },
          async () => {
            const cards = await generateSkeleton(
              picked.block.latexFragment
            );
            const md = cards
              .map(
                (c, i) =>
                  `### Strategy ${i + 1}: ${c.strategy}\n\n${c.description}\n\n` +
                  `**Required lemmas:** ${c.required_lemmas.join(", ") || "None"}\n\n` +
                  `**Check:** ${c.assumptions_to_check.join(", ") || "None"}`
              )
              .join("\n\n---\n\n");

            const doc = await vscode.workspace.openTextDocument({
              content: md,
              language: "markdown",
            });
            await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
          }
        );
      }
    ),

    vscode.commands.registerCommand("mathWithLlm.convertToLean", async () => {
      const blocks = outlineProvider.getBlocks();
      if (blocks.length === 0) {
        vscode.window.showWarningMessage("No LaTeX blocks found.");
        return;
      }

      const items = blocks.map((b) => ({
        label: `${b.type}: ${b.title || b.id}`,
        block: b,
      }));
      const picked = await vscode.window.showQuickPick(items, {
        placeHolder: "Select a block to convert to Lean 4",
      });
      if (!picked) {
        return;
      }

      await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: "Converting to Lean 4...",
        },
        async () => {
          const result = await generateLean(picked.block.latexFragment);
          const content = [
            result.imports.map((i) => `import ${i}`).join("\n"),
            "",
            result.lean_code,
            "",
            `-- Notes: ${result.notes}`,
          ].join("\n");

          const doc = await vscode.workspace.openTextDocument({
            content,
            language: "lean4",
          });
          await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
        }
      );
    }),

    vscode.commands.registerCommand(
      "mathWithLlm.sendBlockToChat",
      (block) => {
        chatProvider.setContext("block", block.latexFragment);
      }
    )
  );
}

export function deactivate() {}
