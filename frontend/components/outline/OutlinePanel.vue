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
        @click="$emit('jump', block.range[0])"
      >
        <span class="block-type">{{ block.type }}</span>
        <span class="block-label">{{ block.label || block.id }}</span>
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
}>()
</script>

<style scoped>
.outline-panel {
  padding: 16px;
  background: #f8f9fa;
  border-right: 1px solid #dee2e6;
  height: 100%;
  overflow-y: auto;
}

h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #495057;
}

.empty {
  color: #6c757d;
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
  cursor: pointer;
  display: flex;
  gap: 8px;
  align-items: center;
  transition: background 0.2s;
}

.block-item:hover {
  background: #e9ecef;
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
  color: #212529;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
