<template>
  <div class="preview-pane-wrapper">
    <div ref="contentRef" class="preview-content" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'

const props = defineProps<{
  source: string
}>()

const contentRef = ref<HTMLElement | null>(null)

let MathJax: any = null

onMounted(async () => {
  // Load MathJax dynamically
  const mathjax = await import('mathjax-full/js/mathjax')
  const { TeX } = await import('mathjax-full/js/input/tex')
  const { CHTML } = await import('mathjax-full/js/output/chtml')
  const { liteAdaptor } = await import('mathjax-full/js/adaptors/liteAdaptor')
  const { RegisterHTMLHandler } = await import('mathjax-full/js/handlers/html')
  const { AllPackages } = await import('mathjax-full/js/input/tex/AllPackages')

  const adaptor = liteAdaptor()
  RegisterHTMLHandler(adaptor)

  MathJax = mathjax.mathjax.document('', {
    InputJax: new TeX({ packages: AllPackages }),
    OutputJax: new CHTML({ fontURL: 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/output/chtml/fonts/woff-v2' })
  })

  await renderContent(props.source)
})

const renderContent = async (source: string) => {
  if (!contentRef.value || !MathJax) return

  // Simple preprocessing: wrap content in a container
  const processed = `<div class="latex-document">${source
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')}</div>`

  contentRef.value.innerHTML = processed

  await nextTick()

  // Typeset with MathJax
  try {
    MathJax.typesetClear([contentRef.value])
    await MathJax.typesetPromise([contentRef.value])
  } catch (e) {
    console.error('MathJax typeset error:', e)
  }
}

watch(
  () => props.source,
  async (newSource) => {
    await renderContent(newSource)
  }
)
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

.latex-error {
  background: #5a1d1d;
  border: 2px solid #f14c4c;
  border-radius: 4px;
  padding: 16px;
  margin: 16px 0;
}

.latex-error strong {
  color: #f48771;
}

.latex-error pre {
  background: #1e1e1e;
  padding: 8px;
  border-radius: 3px;
  overflow-x: auto;
  margin: 8px 0;
  color: #d4d4d4;
  font-size: 12px;
}
</style>
