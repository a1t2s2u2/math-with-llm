import * as vscode from "vscode";

export class PreviewPanelProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = "mathWithLlm.preview";

  private view?: vscode.WebviewView;
  private debounceTimer: ReturnType<typeof setTimeout> | undefined;

  constructor(private readonly extensionUri: vscode.Uri) {}

  resolveWebviewView(webviewView: vscode.WebviewView) {
    this.view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [
        vscode.Uri.joinPath(this.extensionUri, "media"),
      ],
    };

    webviewView.webview.html = this.getHtml(webviewView.webview);

    vscode.window.onDidChangeActiveTextEditor((editor) => {
      if (editor && this.isTexFile(editor.document)) {
        this.updatePreview(editor.document.getText());
      }
    });

    vscode.workspace.onDidChangeTextDocument((e) => {
      if (
        this.isTexFile(e.document) &&
        vscode.window.activeTextEditor?.document === e.document
      ) {
        this.debouncedUpdate(e.document.getText());
      }
    });

    if (vscode.window.activeTextEditor) {
      const doc = vscode.window.activeTextEditor.document;
      if (this.isTexFile(doc)) {
        this.updatePreview(doc.getText());
      }
    }
  }

  private isTexFile(doc: vscode.TextDocument): boolean {
    return doc.languageId === "latex" || doc.fileName.endsWith(".tex");
  }

  private debouncedUpdate(source: string) {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }
    this.debounceTimer = setTimeout(() => this.updatePreview(source), 300);
  }

  private updatePreview(source: string) {
    this.view?.webview.postMessage({ type: "update", content: source });
  }

  private getHtml(webview: vscode.Webview): string {
    const cssUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this.extensionUri, "media", "preview.css")
    );
    const jsUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this.extensionUri, "media", "preview.js")
    );
    const katexCssUri =
      "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css";
    const katexJsUri =
      "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js";

    return /* html */ `<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="${katexCssUri}">
  <link rel="stylesheet" href="${cssUri}">
</head>
<body>
  <div id="preview" class="preview-content"></div>
  <script src="${katexJsUri}"></script>
  <script src="${jsUri}"></script>
</body>
</html>`;
  }
}
