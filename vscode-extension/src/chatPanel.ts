import * as vscode from "vscode";
import { chatStream } from "./llm";

export class ChatPanelProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = "mathWithLlm.chat";

  private view?: vscode.WebviewView;
  private contextType: "block" | "selection" | null = null;
  private contextContent: string | null = null;

  constructor(private readonly extensionUri: vscode.Uri) {}

  setContext(type: "block" | "selection", content: string) {
    this.contextType = type;
    this.contextContent = content;
    this.view?.webview.postMessage({
      type: "contextSet",
      contextType: type,
      content: content.slice(0, 200),
    });
  }

  resolveWebviewView(webviewView: vscode.WebviewView) {
    this.view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [
        vscode.Uri.joinPath(this.extensionUri, "media"),
      ],
    };

    webviewView.webview.html = this.getHtml(webviewView.webview);

    webviewView.webview.onDidReceiveMessage(async (message) => {
      if (message.type === "sendMessage") {
        await this.handleChat(message.text);
      } else if (message.type === "clearContext") {
        this.contextType = null;
        this.contextContent = null;
      }
    });
  }

  private async handleChat(text: string) {
    const webview = this.view?.webview;
    if (!webview) {
      return;
    }

    webview.postMessage({ type: "streamStart" });

    try {
      const stream = chatStream(text, this.contextType, this.contextContent);
      for await (const chunk of stream) {
        webview.postMessage({ type: "streamChunk", content: chunk });
      }
      webview.postMessage({ type: "streamEnd" });
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      webview.postMessage({ type: "streamError", error: msg });
    }
  }

  private getHtml(webview: vscode.Webview): string {
    const cssUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this.extensionUri, "media", "chat.css")
    );
    const jsUri = webview.asWebviewUri(
      vscode.Uri.joinPath(this.extensionUri, "media", "chat.js")
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
  <div id="context-bar" class="context-bar hidden">
    <span id="context-label"></span>
    <button id="clear-context" title="Clear context">&times;</button>
  </div>
  <div id="messages" class="messages"></div>
  <div class="input-area">
    <textarea id="input" placeholder="質問を入力..." rows="1"></textarea>
    <button id="send-btn" title="Send">&#9654;</button>
  </div>
  <script src="${katexJsUri}"></script>
  <script src="${jsUri}"></script>
</body>
</html>`;
  }
}
