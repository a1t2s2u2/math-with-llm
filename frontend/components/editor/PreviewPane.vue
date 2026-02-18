<template>
  <div ref="wrapperRef" class="preview-pane-wrapper">
    <div class="preview-content" v-html="renderedHtml" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  renderedHtml: string
  scrollLine?: number
  syncEnabled?: boolean
}>()

const emit = defineEmits<{
  scroll: [lineNumber: number]
}>()

const wrapperRef = ref<HTMLElement | null>(null)
const isScrollingProgrammatically = ref(false)

// 最も近いdata-line属性を持つ要素を探してスクロール
const scrollToLine = (targetLine: number) => {
  if (!wrapperRef.value) return

  const elements = wrapperRef.value.querySelectorAll('[data-line]')
  if (elements.length === 0) return

  let closestElement: Element | null = null
  let closestDistance = Infinity

  elements.forEach((el) => {
    const line = parseInt(el.getAttribute('data-line') || '0', 10)
    if (line > 0 && line <= targetLine) {
      const distance = targetLine - line
      if (distance < closestDistance) {
        closestDistance = distance
        closestElement = el
      }
    }
  })

  if (closestElement) {
    isScrollingProgrammatically.value = true
    const wrapper = wrapperRef.value
    const elementTop = (closestElement as HTMLElement).offsetTop
    wrapper.scrollTop = Math.max(0, elementTop - 16)
    // スクロール完了後にフラグをリセット
    setTimeout(() => {
      isScrollingProgrammatically.value = false
    }, 50)
  }
}

// 現在のスクロール位置から行番号を取得
const getLineFromScrollPosition = (): number => {
  if (!wrapperRef.value) return 1

  const wrapper = wrapperRef.value
  const scrollTop = wrapper.scrollTop
  const elements = wrapper.querySelectorAll('[data-line]')

  let closestLine = 1
  let closestDistance = Infinity

  elements.forEach((el) => {
    const line = parseInt(el.getAttribute('data-line') || '0', 10)
    if (line > 0) {
      const elementTop = (el as HTMLElement).offsetTop
      const distance = Math.abs(elementTop - scrollTop - 16)
      if (distance < closestDistance) {
        closestDistance = distance
        closestLine = line
      }
    }
  })

  return closestLine
}

// ユーザーのスクロールイベントを処理
const onScroll = () => {
  if (isScrollingProgrammatically.value || !props.syncEnabled) return
  const line = getLineFromScrollPosition()
  if (line > 0) {
    emit('scroll', line)
  }
}

onMounted(() => {
  wrapperRef.value?.addEventListener('scroll', onScroll)
})

onUnmounted(() => {
  wrapperRef.value?.removeEventListener('scroll', onScroll)
})

watch(
  () => props.scrollLine,
  (line) => {
    if (props.syncEnabled && line !== undefined && line > 0) {
      scrollToLine(line)
    }
  }
)

// HTML変更時にスクロール位置を再適用
watch(
  () => props.renderedHtml,
  async () => {
    await nextTick()
    if (props.scrollLine !== undefined && props.scrollLine > 0) {
      scrollToLine(props.scrollLine)
    }
  }
)
</script>

<style scoped>
.preview-pane-wrapper {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
  background: var(--color-bg-main);
  min-height: 0;
}

.preview-content {
  line-height: 1.8;
  font-family: 'Times New Roman', serif;
  font-size: 20px;
  color: var(--color-text);
}

.preview-content p {
  margin-bottom: 14px;
}

/* Theorem environments */
.preview-content :deep(.latex-env) {
  margin: 18px 0;
  padding: 14px;
  border-left: 3px solid var(--color-accent);
  background: var(--color-bg-secondary);
  border-radius: 4px;
}

.preview-content :deep(.env-heading) {
  font-weight: bold;
  font-size: 18px;
  color: var(--color-accent);
  margin-bottom: 8px;
}

.preview-content :deep(.env-content) {
  font-size: 19px;
  line-height: 1.6;
  color: var(--color-text);
}

/* Proof environment */
.preview-content :deep(.latex-env.proof) {
  border-left-color: #888;
  background: var(--color-bg-secondary);
}

.preview-content :deep(.proof .env-heading) {
  font-style: italic;
  color: var(--color-text-muted);
}

/* Lists */
.preview-content :deep(.latex-list) {
  margin: 12px 0;
  padding-left: 24px;
  color: var(--color-text);
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
  color: var(--color-accent);
  border-bottom: 2px solid #3e3e3e;
  padding-bottom: 8px;
}

.preview-content :deep(.latex-subsection) {
  font-size: 20px;
  font-weight: bold;
  margin: 20px 0 12px 0;
  color: var(--color-accent);
}

.preview-content :deep(.latex-subsubsection) {
  font-size: 18px;
  font-weight: bold;
  margin: 16px 0 10px 0;
  color: var(--color-accent);
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
  color: var(--color-accent);
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
.preview-content :deep(.katex) {
  font-size: 1.15em;
}

.preview-content :deep(.display-math) {
  margin: 16px 0;
  text-align: center;
  color: var(--color-math);
}

.preview-content :deep(.display-math math) {
  color: var(--color-math);
}

.preview-content :deep(.display-math .katex) {
  font-size: 1.3em;
}

.preview-content :deep(.inline-math) {
  display: inline;
  color: var(--color-math);
}

.preview-content :deep(.inline-math math) {
  color: var(--color-math);
}

/* KaTeX overflow handling */
.preview-content :deep(.katex-display) {
  overflow-x: auto;
  overflow-y: hidden;
  padding: 4px 0;
}

.preview-content :deep(.katex-display > .katex) {
  white-space: nowrap;
}
</style>
