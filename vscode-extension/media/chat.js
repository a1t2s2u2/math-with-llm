// @ts-check
(function () {
  // @ts-ignore
  const vscode = acquireVsCodeApi();

  const messagesEl = document.getElementById("messages");
  const inputEl = document.getElementById("input");
  const sendBtn = document.getElementById("send-btn");
  const contextBar = document.getElementById("context-bar");
  const contextLabel = document.getElementById("context-label");
  const clearContextBtn = document.getElementById("clear-context");

  let currentAssistantEl = null;
  let currentContent = "";

  function renderMath(text) {
    const placeholders = new Map();
    let counter = 0;
    let result = text;

    function replaceWith(math, displayMode) {
      const id = `\x00MATH_${counter++}\x00`;
      try {
        // @ts-ignore
        placeholders.set(id, katex.renderToString(math.trim(), {
          throwOnError: false,
          displayMode: displayMode,
        }));
      } catch {
        placeholders.set(id, displayMode ? `$$${math}$$` : `$${math}$`);
      }
      return id;
    }

    result = result.replace(/\\\[([\s\S]+?)\\\]/g, (_, m) => replaceWith(m, true));
    result = result.replace(/\$\$([\s\S]+?)\$\$/g, (_, m) => replaceWith(m, true));
    result = result.replace(/\\\(([\s\S]+?)\\\)/g, (_, m) => replaceWith(m, false));
    result = result.replace(/\$([^$\n]+?)\$/g, (_, m) => replaceWith(m, false));

    // Convert newlines to <br>
    result = result.replace(/\n/g, "<br>");

    for (const [id, html] of placeholders) {
      result = result.replaceAll(id, html);
    }

    return result;
  }

  function addMessage(role, content) {
    const div = document.createElement("div");
    div.className = `message ${role}`;
    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";
    contentDiv.innerHTML = renderMath(content);
    div.appendChild(contentDiv);
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return contentDiv;
  }

  function send() {
    const text = inputEl.value.trim();
    if (!text) return;

    addMessage("user", text);
    inputEl.value = "";
    inputEl.style.height = "36px";
    vscode.postMessage({ type: "sendMessage", text });
  }

  sendBtn.addEventListener("click", send);
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  });
  inputEl.addEventListener("input", () => {
    inputEl.style.height = "36px";
    inputEl.style.height = Math.min(inputEl.scrollHeight, 100) + "px";
  });

  clearContextBtn.addEventListener("click", () => {
    contextBar.classList.add("hidden");
    vscode.postMessage({ type: "clearContext" });
  });

  window.addEventListener("message", (event) => {
    const msg = event.data;
    switch (msg.type) {
      case "streamStart": {
        const div = document.createElement("div");
        div.className = "message assistant";
        const contentDiv = document.createElement("div");
        contentDiv.className = "message-content";
        const spinner = document.createElement("span");
        spinner.className = "spinner";
        contentDiv.appendChild(spinner);
        div.appendChild(contentDiv);
        messagesEl.appendChild(div);
        messagesEl.scrollTop = messagesEl.scrollHeight;
        currentAssistantEl = contentDiv;
        currentContent = "";
        break;
      }
      case "streamChunk":
        if (currentAssistantEl) {
          currentContent += msg.content;
          currentAssistantEl.innerHTML = renderMath(currentContent);
          messagesEl.scrollTop = messagesEl.scrollHeight;
        }
        break;
      case "streamEnd":
        currentAssistantEl = null;
        break;
      case "streamError":
        if (currentAssistantEl) {
          currentAssistantEl.innerHTML = `<span class="error-message">Error: ${msg.error}</span>`;
        }
        currentAssistantEl = null;
        break;
      case "contextSet":
        contextBar.classList.remove("hidden");
        contextLabel.textContent = `Context (${msg.contextType}): ${msg.content}`;
        break;
    }
  });
})();
