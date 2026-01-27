<template>
  <div class="symbol-table">
    <h3>Symbols</h3>
    <div v-if="symbols.length === 0" class="empty">No symbols found</div>
    <div v-else class="symbol-list">
      <div
        v-for="symbol in symbols"
        :key="symbol.name"
        class="symbol-item"
        @click="$emit('jump', symbol.first_occurrence_pos)"
      >
        <span class="symbol-name">{{ symbol.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Symbol } from '~/types/api'

defineProps<{
  symbols: Symbol[]
}>()

defineEmits<{
  jump: [position: number]
}>()
</script>

<style scoped>
.symbol-table {
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

.symbol-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.symbol-item {
  padding: 6px 12px;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.symbol-item:hover {
  border-color: #198754;
  background: #d1e7dd;
}

.symbol-name {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  font-weight: 600;
  color: #198754;
}
</style>
