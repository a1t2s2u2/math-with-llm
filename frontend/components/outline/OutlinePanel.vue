<template>
  <div class="outline-panel">
    <div v-if="blocks.length === 0" class="empty">No blocks found</div>
    <div v-else class="block-list">
      <div
        v-for="block in blocks"
        :key="block.id"
        class="block-item"
        :class="[`block-${block.type}`, { selected: selectedId === block.id }]"
        @click="handleClick(block)"
      >
        <span class="block-type">{{ formatType(block.type) }}</span>
        <span v-if="block.title" class="block-title" v-html="renderMath(block.title)" />
        <span v-if="block.label" class="block-label">{{ block.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Block } from '~/types/api'
import { useMathRender } from '~/composables/useMathRender'
import { BLOCK_TYPE_SHORT } from '~/utils/constants'

defineProps<{
  blocks: Block[]
}>()

const emit = defineEmits<{
  jump: [position: number]
  selectBlock: [block: Block]
  deselectBlock: []
}>()

const selectedId = ref<string | null>(null)

const { renderMath } = useMathRender()

const handleClick = (block: Block) => {
  if (selectedId.value === block.id) {
    // 同じブロックをクリック → 選択解除
    selectedId.value = null
    emit('deselectBlock')
  } else {
    // 別のブロックをクリック → 選択
    selectedId.value = block.id
    emit('jump', block.range[0])
    emit('selectBlock', block)
  }
}

const formatType = (type: string) => {
  return BLOCK_TYPE_SHORT[type] || type
}
</script>

<style scoped>
.outline-panel {
  padding: 8px;
  background: var(--color-bg-main);
  height: 100%;
  overflow-y: auto;
}

.empty {
  color: var(--color-text-dimmed);
  font-size: var(--font-size-sm);
  padding: 8px;
}

.block-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.block-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
  border-left: 3px solid transparent;
}

.block-item:hover {
  background: var(--color-bg-secondary);
}

.block-item.selected {
  background: var(--color-selected);
}

.block-definition {
  border-left-color: #0d6efd;
}

.block-theorem,
.block-lemma,
.block-proposition,
.block-corollary {
  border-left-color: #198754;
}

.block-proof {
  border-left-color: #ffc107;
}

.block-remark,
.block-example {
  border-left-color: #6c757d;
}

.block-type {
  flex-shrink: 0;
  font-size: var(--font-size-xs);
  font-weight: 600;
  padding: 1px 4px;
  border-radius: 2px;
  background: var(--color-bg-hover);
  color: var(--color-text-secondary);
}

.block-definition .block-type {
  background: #0d6efd20;
  color: #0d6efd;
}

.block-theorem .block-type,
.block-lemma .block-type,
.block-proposition .block-type,
.block-corollary .block-type {
  background: #19875420;
  color: #198754;
}

.block-proof .block-type {
  background: #b8860b20;
  color: #b8860b;
}

.block-label {
  flex-shrink: 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  font-family: monospace;
}

.block-title {
  flex: 1;
  min-width: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.block-title :deep(.katex) {
  font-size: 1em;
}
</style>
