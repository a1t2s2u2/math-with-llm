<template>
  <div class="preview-pane-wrapper">
    <div class="preview-content" v-html="renderedHtml" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import katex from 'katex'

const props = defineProps<{
  source: string
}>()

const renderedHtml = ref('')

const renderLatex = (source: string) => {
  let html = source

  // Extract custom commands defined with \newcommand
  const customCommands: Record<string, string> = {}
  html = html.replace(/\\newcommand\{\\([^}]+)\}\{([^}]+)\}/g, (match, name, replacement) => {
    customCommands[name] = replacement
    return ''
  })

  // Remove LaTeX preamble commands (they define structure but don't render content)
  html = html.replace(/\\documentclass(\[.*?\])?\{.*?\}/g, '')
  html = html.replace(/\\usepackage(\[.*?\])?\{.*?\}/g, '')
  html = html.replace(/\\newtheorem\{.*?\}(\[.*?\])?\{.*?\}(\[.*?\])?/g, '')
  html = html.replace(/\\theoremstyle\{.*?\}/g, '')
  html = html.replace(/\\title\{.*?\}/g, '')
  html = html.replace(/\\author\{.*?\}/g, '')
  html = html.replace(/\\date\{.*?\}/g, '')
  html = html.replace(/\\maketitle/g, '')

  // Remove document environment markers
  html = html.replace(/\\begin\{document\}/g, '')
  html = html.replace(/\\end\{document\}/g, '')

  // Remove comments (lines starting with %)
  html = html.replace(/^%.*$/gm, '')

  // Apply custom commands
  for (const [name, replacement] of Object.entries(customCommands)) {
    const regex = new RegExp(`\\\\${name}\\b`, 'g')
    html = html.replace(regex, replacement)
  }

  // Handle \section commands
  html = html.replace(/\\section\{([^}]+)\}/g, '<h2 class="latex-section">$1</h2>')
  html = html.replace(/\\subsection\{([^}]+)\}/g, '<h3 class="latex-subsection">$1</h3>')
  html = html.replace(/\\subsubsection\{([^}]+)\}/g, '<h4 class="latex-subsubsection">$1</h4>')

  // Remove \displaystyle (it's handled by KaTeX automatically in display mode)
  html = html.replace(/\\displaystyle\s*/g, '')

  // Display math blocks: \[...\]
  html = html.replace(/\\\[([\s\S]+?)\\\]/g, (match, tex) => {
    try {
      return katex.renderToString(tex, { displayMode: true, throwOnError: false })
    } catch {
      return match
    }
  })

  // Display math: $$...$$
  html = html.replace(/\$\$([\s\S]+?)\$\$/g, (match, tex) => {
    try {
      return katex.renderToString(tex, { displayMode: true, throwOnError: false })
    } catch {
      return match
    }
  })

  // Inline math: $...$
  html = html.replace(/\$([^\n]+?)\$/g, (match, tex) => {
    try {
      return katex.renderToString(tex, { displayMode: false, throwOnError: false })
    } catch {
      return match
    }
  })

  // LaTeX enumerate environment
  html = html.replace(/\\begin\{enumerate\}([\s\S]*?)\\end\{enumerate\}/g, (match, content) => {
    const items = content.split(/\\item\s+/).filter((item: string) => item.trim())
    const listItems = items.map((item: string) => `<li>${item.trim()}</li>`).join('')
    return `<ol class="latex-list">${listItems}</ol>`
  })

  // LaTeX itemize environment
  html = html.replace(/\\begin\{itemize\}([\s\S]*?)\\end\{itemize\}/g, (match, content) => {
    const items = content.split(/\\item\s+/).filter((item: string) => item.trim())
    const listItems = items.map((item: string) => `<li>${item.trim()}</li>`).join('')
    return `<ul class="latex-list">${listItems}</ul>`
  })

  // Text formatting commands
  html = html.replace(/\\emph\{([^}]+)\}/g, '<em>$1</em>')
  html = html.replace(/\\textbf\{([^}]+)\}/g, '<strong>$1</strong>')
  html = html.replace(/\\textit\{([^}]+)\}/g, '<em>$1</em>')
  html = html.replace(/\\texttt\{([^}]+)\}/g, '<code>$1</code>')

  // Labels and refs (just remove them for now)
  html = html.replace(/\\label\{[^}]+\}/g, '')
  html = html.replace(/\\ref\{[^}]+\}/g, '[ref]')

  // Other LaTeX environments (display as blocks)
  html = html.replace(/\\begin\{([^}]+)\}([\s\S]*?)\\end\{\1\}/g, (match, env, content) => {
    return `<div class="latex-env latex-${env}">
      <div class="env-type">${env}</div>
      <div class="env-content">${content.trim()}</div>
    </div>`
  })

  // Line breaks
  html = html.replace(/\n\n+/g, '</p><p>')
  html = html.replace(/\n/g, '<br>')

  renderedHtml.value = `<p>${html}</p>`
}

watch(() => props.source, (newSource) => {
  renderLatex(newSource)
}, { immediate: true })

onMounted(() => {
  renderLatex(props.source)
})
</script>

<style>
@import 'katex/dist/katex.min.css';
</style>

<style scoped>
.preview-pane-wrapper {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
  background: #1e1e1e;
  min-height: 0;
}

.preview-content {
  line-height: 1.8;
  font-family: 'Times New Roman', serif;
  font-size: 16px;
  color: #d4d4d4;
}

.preview-content p {
  margin-bottom: 12px;
}

.latex-env {
  margin: 16px 0;
  padding: 12px;
  border-left: 3px solid #4ec9b0;
  background: #2d2d2d;
}

.env-type {
  font-weight: bold;
  font-size: 14px;
  color: #4ec9b0;
  margin-bottom: 8px;
  text-transform: capitalize;
}

.env-content {
  font-size: 15px;
  line-height: 1.6;
  color: #d4d4d4;
}

.latex-list {
  margin: 12px 0;
  padding-left: 24px;
  color: #d4d4d4;
}

.latex-list li {
  margin: 8px 0;
  line-height: 1.6;
}

.preview-content em {
  font-style: italic;
  color: #dcdcaa;
}

.preview-content strong {
  font-weight: bold;
  color: #4ec9b0;
}

.preview-content code {
  font-family: 'Monaco', 'Courier New', monospace;
  background: #2d2d2d;
  padding: 2px 6px;
  border-radius: 3px;
  color: #ce9178;
}

.latex-section {
  font-size: 24px;
  font-weight: bold;
  margin: 24px 0 16px 0;
  color: #4ec9b0;
  border-bottom: 2px solid #3e3e3e;
  padding-bottom: 8px;
}

.latex-subsection {
  font-size: 20px;
  font-weight: bold;
  margin: 20px 0 12px 0;
  color: #4ec9b0;
}

.latex-subsubsection {
  font-size: 18px;
  font-weight: bold;
  margin: 16px 0 10px 0;
  color: #4ec9b0;
}
</style>
