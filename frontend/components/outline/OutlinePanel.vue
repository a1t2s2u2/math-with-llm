<template>
  <div class="outline-panel">
    <div v-if="blocks.length === 0" class="empty">No blocks found</div>
    <div v-else class="block-list">
      <div
        v-for="block in blocks"
        :key="block.id"
        class="block-item"
        :class="`block-${block.type}`"
        @click="$emit('jump', block.range[0])"
      >
        <div class="block-header">
          <span class="block-type">{{ formatType(block.type) }}</span>
          <span v-if="block.label" class="block-label">{{ block.label }}</span>
        </div>
        <div v-if="block.title" class="block-title">{{ block.title }}</div>
        <div class="block-actions">
          <button
            class="action-button"
            title="証明戦略を生成"
            @click.stop="$emit('generateSkeleton', block.id)"
          >
            💡
          </button>
          <button
            class="action-button"
            title="Leanコードを生成"
            @click.stop="$emit('generateLean', block.id)"
          >
            ⚡
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Block } from '~/types/api'

defineProps<{
  blocks: Block[]
}>()

defineEmits<{
  jump: [position: number]
  generateSkeleton: [blockId: string]
  generateLean: [blockId: string]
}>()

const formatType = (type: string) => {
  const typeMap: Record<string, string> = {
    definition: 'Def',
    theorem: 'Thm',
    lemma: 'Lem',
    proposition: 'Prop',
    corollary: 'Cor',
    proof: 'Prf',
    remark: 'Rem',
    example: 'Ex'
  }
  return typeMap[type] || type
}
</script>

<style scoped>
.outline-panel {
  padding: 8px;
  background: #1e1e1e;
  height: 100%;
  overflow-y: auto;
}

.empty {
  color: #858585;
  font-size: 12px;
  padding: 8px;
}

.block-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.block-item {
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
  border-left: 3px solid transparent;
}

.block-item:hover {
  background: #2d2d2d;
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

.block-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 2px;
}

.block-type {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  padding: 1px 4px;
  border-radius: 2px;
  background: #3e3e3e;
  color: #cccccc;
}

.block-definition .block-type {
  background: #0d6efd33;
  color: #6cb2f7;
}

.block-theorem .block-type,
.block-lemma .block-type,
.block-proposition .block-type,
.block-corollary .block-type {
  background: #19875433;
  color: #6fcf97;
}

.block-proof .block-type {
  background: #ffc10733;
  color: #ffd966;
}

.block-label {
  font-size: 11px;
  color: #808080;
  font-family: monospace;
}

.block-title {
  font-size: 12px;
  color: #d4d4d4;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.block-actions {
  display: flex;
  gap: 4px;
  margin-top: 4px;
  opacity: 0;
  transition: opacity 0.15s;
}

.block-item:hover .block-actions {
  opacity: 1;
}

.action-button {
  padding: 2px 6px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  background: #3e3e3e;
  transition: background 0.15s;
}

.action-button:hover {
  background: #4e4e4e;
}
</style>
