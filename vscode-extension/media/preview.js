// @ts-check
(function () {
  const previewEl = document.getElementById("preview");

  const ENV_NAMES = {
    definition: "Definition",
    lemma: "Lemma",
    theorem: "Theorem",
    proposition: "Proposition",
    corollary: "Corollary",
    proof: "Proof",
    remark: "Remark",
    example: "Example",
  };

  const BLOCK_TYPES = Object.keys(ENV_NAMES).join("|");

  function renderKatex(math, displayMode) {
    try {
      // @ts-ignore
      return katex.renderToString(math.trim(), {
        throwOnError: false,
        displayMode: displayMode,
      });
    } catch {
      return displayMode ? `$$${math}$$` : `$${math}$`;
    }
  }

  function processLatex(source) {
    let result = source;

    // Process theorem environments
    const envPattern = new RegExp(
      `\\\\begin\\{(${BLOCK_TYPES})\\}(\\[[^\\]]*\\])?([\\s\\S]*?)\\\\end\\{\\1\\}`,
      "g"
    );
    result = result.replace(envPattern, (_, type, opt, content) => {
      const name = ENV_NAMES[type] || type;
      const title = opt ? ` ${opt.slice(1, -1)}` : "";
      const cssClass = type === "proof" ? "latex-env proof" : "latex-env";
      const inner = processInlineMath(content.trim());
      return `<div class="${cssClass}"><div class="env-heading">${name}${title}</div><div class="env-content">${inner}</div></div>`;
    });

    // Sections
    result = result.replace(
      /\\section\{([^}]+)\}/g,
      '<div class="latex-section">$1</div>'
    );
    result = result.replace(
      /\\subsection\{([^}]+)\}/g,
      '<div class="latex-subsection">$1</div>'
    );
    result = result.replace(
      /\\subsubsection\{([^}]+)\}/g,
      '<div class="latex-subsubsection">$1</div>'
    );

    // Remove \label{...}
    result = result.replace(/\\label\{[^}]*\}/g, "");

    // Process math
    result = processInlineMath(result);

    // Paragraphs
    result = result.replace(/\n\n+/g, "</p><p>");
    result = `<p>${result}</p>`;

    return result;
  }

  function processInlineMath(text) {
    const placeholders = new Map();
    let counter = 0;
    let result = text;

    function replaceWith(math, displayMode) {
      const id = `\x00MATH_${counter++}\x00`;
      placeholders.set(id, renderKatex(math, displayMode));
      return id;
    }

    // Display math
    result = result.replace(
      /\\\[([\s\S]+?)\\\]/g,
      (_, m) => replaceWith(m, true)
    );
    result = result.replace(
      /\$\$([\s\S]+?)\$\$/g,
      (_, m) => replaceWith(m, true)
    );

    // Inline math
    result = result.replace(
      /\\\(([\s\S]+?)\\\)/g,
      (_, m) => replaceWith(m, false)
    );
    result = result.replace(
      /\$([^$\n]+?)\$/g,
      (_, m) => replaceWith(m, false)
    );

    for (const [id, html] of placeholders) {
      result = result.replaceAll(id, html);
    }

    return result;
  }

  window.addEventListener("message", (event) => {
    const msg = event.data;
    if (msg.type === "update") {
      previewEl.innerHTML = processLatex(msg.content);
    }
  });
})();
