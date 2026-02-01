import * as vscode from "vscode";
import { Block, BlockType, extractBlocks } from "./parser";

const BLOCK_ICONS: Record<BlockType, vscode.ThemeIcon> = {
  definition: new vscode.ThemeIcon("symbol-class"),
  lemma: new vscode.ThemeIcon("symbol-method"),
  theorem: new vscode.ThemeIcon("symbol-key"),
  proposition: new vscode.ThemeIcon("symbol-interface"),
  corollary: new vscode.ThemeIcon("symbol-event"),
  proof: new vscode.ThemeIcon("symbol-operator"),
  remark: new vscode.ThemeIcon("symbol-text"),
  example: new vscode.ThemeIcon("symbol-snippet"),
};

export class BlockOutlineProvider implements vscode.TreeDataProvider<Block> {
  private _onDidChangeTreeData = new vscode.EventEmitter<
    Block | undefined | void
  >();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

  private blocks: Block[] = [];
  private currentDocument: vscode.TextDocument | undefined;

  constructor() {
    vscode.window.onDidChangeActiveTextEditor((editor) => {
      if (editor && this.isTexFile(editor.document)) {
        this.parseDocument(editor.document);
      }
    });

    vscode.workspace.onDidChangeTextDocument((e) => {
      if (this.isTexFile(e.document) && e.document === this.currentDocument) {
        this.parseDocument(e.document);
      }
    });

    if (vscode.window.activeTextEditor) {
      const doc = vscode.window.activeTextEditor.document;
      if (this.isTexFile(doc)) {
        this.parseDocument(doc);
      }
    }
  }

  private isTexFile(doc: vscode.TextDocument): boolean {
    return doc.languageId === "latex" || doc.fileName.endsWith(".tex");
  }

  private parseDocument(document: vscode.TextDocument) {
    this.currentDocument = document;
    this.blocks = extractBlocks(document.getText());
    this._onDidChangeTreeData.fire();
  }

  getBlocks(): Block[] {
    return this.blocks;
  }

  getTreeItem(block: Block): vscode.TreeItem {
    const typeLabel = block.type.charAt(0).toUpperCase() + block.type.slice(1);
    const label = block.title ? `${typeLabel}: ${block.title}` : typeLabel;

    const item = new vscode.TreeItem(label, vscode.TreeItemCollapsibleState.None);
    item.iconPath = BLOCK_ICONS[block.type];
    item.tooltip = block.latexFragment.slice(0, 200);
    item.description = block.label ?? undefined;
    item.command = {
      command: "mathWithLlm.revealBlock",
      title: "Reveal Block",
      arguments: [block],
    };
    return item;
  }

  getChildren(): Block[] {
    return this.blocks;
  }

  revealBlock(block: Block) {
    const editor = vscode.window.activeTextEditor;
    if (!editor || !this.currentDocument) {
      return;
    }
    const startPos = this.currentDocument.positionAt(block.range[0]);
    const endPos = this.currentDocument.positionAt(block.range[1]);
    const range = new vscode.Range(startPos, endPos);
    editor.selection = new vscode.Selection(startPos, startPos);
    editor.revealRange(range, vscode.TextEditorRevealType.InCenter);
  }
}
