<template>
  <div class="preview-pane-wrapper">
    <div ref="contentRef" class="preview-content" v-html="renderedHtml" />
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  renderedHtml: string
}>()
</script>

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

/* Theorem environments */
.preview-content :deep(.latex-env) {
  margin: 16px 0;
  padding: 12px;
  border-left: 3px solid #4ec9b0;
  background: #2d2d2d;
  border-radius: 4px;
}

.preview-content :deep(.env-heading) {
  font-weight: bold;
  font-size: 14px;
  color: #4ec9b0;
  margin-bottom: 8px;
}

.preview-content :deep(.env-content) {
  font-size: 15px;
  line-height: 1.6;
  color: #d4d4d4;
}

/* Proof environment */
.preview-content :deep(.latex-env.proof) {
  border-left-color: #888;
  background: #252525;
}

.preview-content :deep(.proof .env-heading) {
  font-style: italic;
  color: #dcdcaa;
}

/* Lists */
.preview-content :deep(.latex-list) {
  margin: 12px 0;
  padding-left: 24px;
  color: #d4d4d4;
}

.preview-content :deep(.latex-list li) {
  margin: 8px 0;
  line-height: 1.6;
}

/* Sections */
.preview-content :deep(.latex-section) {
  font-size: 24px;
  font-weight: bold;
  margin: 24px 0 16px 0;
  color: #4ec9b0;
  border-bottom: 2px solid #3e3e3e;
  padding-bottom: 8px;
}

.preview-content :deep(.latex-subsection) {
  font-size: 20px;
  font-weight: bold;
  margin: 20px 0 12px 0;
  color: #4ec9b0;
}

.preview-content :deep(.latex-subsubsection) {
  font-size: 18px;
  font-weight: bold;
  margin: 16px 0 10px 0;
  color: #4ec9b0;
}

/* Document title block */
.preview-content :deep(.latex-title-block) {
  text-align: center;
  margin: 32px 0 48px 0;
  padding: 24px 0;
  border-bottom: 1px solid #3e3e3e;
}

.preview-content :deep(.latex-title) {
  font-size: 28px;
  font-weight: bold;
  color: #4ec9b0;
  margin-bottom: 16px;
  line-height: 1.3;
}

.preview-content :deep(.latex-author) {
  font-size: 16px;
  color: #b0b0b0;
  margin-bottom: 8px;
  font-style: italic;
}

.preview-content :deep(.latex-date) {
  font-size: 14px;
  color: #888;
  margin-top: 8px;
}

/* Math display */
.preview-content :deep(.display-math) {
  margin: 16px 0;
  text-align: center;
}

.preview-content :deep(.inline-math) {
  display: inline;
}
</style>
