<template>
  <div class="preview-pane">
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

  // LaTeX environments (display as blocks)
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
.preview-pane {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
  background: #ffffff;
}

.preview-content {
  line-height: 1.8;
  font-family: 'Times New Roman', serif;
  font-size: 16px;
}

.preview-content p {
  margin-bottom: 12px;
}

.latex-env {
  margin: 16px 0;
  padding: 12px;
  border-left: 3px solid #007acc;
  background: #f8f9fa;
}

.env-type {
  font-weight: bold;
  font-size: 14px;
  color: #007acc;
  margin-bottom: 8px;
  text-transform: capitalize;
}

.env-content {
  font-size: 15px;
  line-height: 1.6;
}
</style>
