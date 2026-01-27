<template>
  <div class="definition-ledger">
    <h3>Definitions</h3>
    <div v-if="definitions.length === 0" class="empty">No definitions found</div>
    <div v-else class="definition-list">
      <div
        v-for="def in definitions"
        :key="def.id"
        class="definition-item"
        @click="$emit('jump', def.range[0])"
      >
        <div class="def-label">{{ def.label || def.id }}</div>
        <div class="def-preview">{{ getPreview(def.latex_fragment) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Block } from '~/types/api'

defineProps<{
  definitions: Block[]
}>()

defineEmits<{
  jump: [position: number]
}>()

const getPreview = (fragment: string) => {
  return fragment.slice(0, 100).replace(/\n/g, ' ') + '...'
}
</script>

<style scoped>
.definition-ledger {
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

.definition-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.definition-item {
  padding: 12px;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.definition-item:hover {
  border-color: #0d6efd;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.def-label {
  font-weight: 600;
  font-size: 13px;
  color: #0d6efd;
  margin-bottom: 4px;
}

.def-preview {
  font-size: 12px;
  color: #6c757d;
  line-height: 1.4;
}
</style>
