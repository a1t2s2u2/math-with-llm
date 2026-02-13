<template>
  <div class="diff-view">
    <div class="diff-header">
      <span class="diff-path">{{ path }}</span>
      <span class="diff-label">{{ staged ? '(Staged)' : '(Working Tree)' }}</span>
      <button class="close-btn" @click="$emit('close')">&times;</button>
    </div>
    <div class="diff-editor">
      <VueMonacoDiffEditor
        :original="oldContent"
        :modified="newContent"
        :options="editorOptions"
        language="latex"
        :theme="editorTheme"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { VueMonacoDiffEditor } from '@guolao/vue-monaco-editor'
import { getGitDiff } from '~/utils/api'
import { useTheme } from '~/composables/useTheme'

const props = defineProps<{
  path: string
  staged: boolean
}>()

defineEmits<{
  close: []
}>()

const { theme } = useTheme()
const editorTheme = computed(() => (theme.value === 'dark' ? 'vs-dark' : 'vs'))

const oldContent = ref('')
const newContent = ref('')

const editorOptions = {
  readOnly: true,
  fontSize: 13,
  fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
  minimap: { enabled: false },
  renderSideBySide: true,
  scrollBeyondLastLine: false
}

const loadDiff = async () => {
  const diff = await getGitDiff(props.path, props.staged)
  oldContent.value = diff.old_content
  newContent.value = diff.new_content
}

watch(() => [props.path, props.staged], loadDiff, { immediate: true })
</script>

<style scoped>
.diff-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.diff-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--color-bg-header);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.diff-path {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.diff-label {
  font-size: 11px;
  color: var(--color-text-muted);
}

.close-btn {
  margin-left: auto;
  background: none;
  border: none;
  color: var(--color-text-muted);
  font-size: 18px;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}

.close-btn:hover {
  color: var(--color-text);
}

.diff-editor {
  flex: 1;
  overflow: hidden;
}
</style>
