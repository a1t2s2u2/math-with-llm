<template>
  <div class="outline-panel">
    <h3>Outline</h3>
    <div v-if="blocks.length === 0" class="empty">No blocks found</div>
    <div v-else class="block-list">
      <div
        v-for="block in blocks"
        :key="block.id"
        class="block-item"
        :class="`block-${block.type}`"
      >
        <div class="block-info" @click="$emit('jump', block.range[0])">
          <span class="block-type">{{ block.type }}</span>
          <span class="block-label">{{ block.label || block.id }}</span>
        </div>
        <div class="block-actions">
          <button
            class="action-button strategy-button"
            @click="$emit('generateSkeleton', block.id)"
            title="証明戦略を生成"
          >
            💡
          </button>
          <button
            class="action-button lean-button"
            @click="$emit('generateLean', block.id)"
            title="Leanコードを生成"
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
</script>

<style scoped>
.outline-panel {
  padding: 16px;
  background: #1e1e1e;
  border-right: 1px solid #3e3e3e;
  height: 100%;
  overflow-y: auto;
}

h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #d4d4d4;
}

.empty {
  color: #858585;
  font-size: 13px;
}

.block-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.block-item {
  padding: 8px 12px;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  transition: background 0.2s;
}

.block-item:hover {
  background: #2d2d2d;
}

.block-info {
  display: flex;
  gap: 8px;
  align-items: center;
  flex: 1;
  cursor: pointer;
}

.block-actions {
  display: flex;
  gap: 4px;
}

.action-button {
  padding: 4px 8px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 14px;
  background: #3e3e3e;
  transition: background 0.2s;
}

.action-button:hover {
  background: #4e4e4e;
}

.strategy-button:hover {
  background: #0d6efd;
}

.lean-button:hover {
  background: #198754;
}

.block-type {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: 3px;
  background: #6c757d;
  color: white;
}

.block-definition .block-type {
  background: #0d6efd;
}

.block-theorem .block-type,
.block-lemma .block-type {
  background: #198754;
}

.block-proof .block-type {
  background: #ffc107;
  color: #000;
}

.block-label {
  font-size: 13px;
  color: #d4d4d4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
