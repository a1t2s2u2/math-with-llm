<template>
  <div class="preview-pane">
    <div class="preview-content" v-html="renderedHtml" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'

const props = defineProps<{
  source: string
}>()

const renderedHtml = ref('')

const renderLatex = (source: string) => {
  const escaped = source
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')

  renderedHtml.value = `<pre>${escaped}</pre>`
}

watch(() => props.source, (newSource) => {
  renderLatex(newSource)
}, { immediate: true })

onMounted(() => {
  renderLatex(props.source)
})
</script>

<style scoped>
.preview-pane {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
  background: #ffffff;
}

.preview-content {
  line-height: 1.6;
}

.preview-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Times New Roman', serif;
  font-size: 16px;
}
</style>
