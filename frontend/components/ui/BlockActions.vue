<template>
  <div class="block-actions">
    <button
      @click="$emit('generate-skeleton')"
      :disabled="loading"
      class="action-btn skeleton-btn"
    >
      📋 Generate Skeleton
    </button>
    <button
      @click="$emit('generate-lean')"
      :disabled="loading"
      class="action-btn lean-btn"
    >
      🔧 Generate Lean
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  loading: boolean
}>()

defineEmits<{
  'generate-skeleton': []
  'generate-lean': []
}>()
</script>

<style scoped>
.block-actions {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  margin: 8px 0;
}

.action-btn {
  padding: 6px 12px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.action-btn:hover:not(:disabled) {
  background: #e9ecef;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.skeleton-btn:hover:not(:disabled) {
  border-color: #007acc;
  color: #007acc;
}

.lean-btn:hover:not(:disabled) {
  border-color: #198754;
  color: #198754;
}
</style>
