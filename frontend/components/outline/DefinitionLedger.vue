<template>
  <div class="definition-ledger">
    <div v-if="definitions.length === 0" class="empty">No definitions found</div>
    <div v-else class="definition-list">
      <div
        v-for="def in definitions"
        :key="def.id"
        class="definition-item"
        @click="$emit('jump', def.range[0])"
      >
        <div class="def-header">
          <span class="def-type">Def</span>
          <span v-if="def.label" class="def-label">{{ def.label }}</span>
        </div>
        <div v-if="def.title" class="def-title" v-html="renderMath(def.title)" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Block } from '~/types/api'
import { useMathRender } from '~/composables/useMathRender'

defineProps<{
  definitions: Block[]
}>()

defineEmits<{
  jump: [position: number]
}>()

const { renderMath } = useMathRender()
</script>

<style scoped>
.definition-ledger {
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

.definition-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.definition-item {
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
  border-left: 3px solid #0d6efd;
}

.definition-item:hover {
  background: #2d2d2d;
}

.def-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 2px;
}

.def-type {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  padding: 1px 4px;
  border-radius: 2px;
  background: #0d6efd33;
  color: #6cb2f7;
}

.def-label {
  font-size: 11px;
  color: #808080;
  font-family: monospace;
}

.def-title {
  font-size: 12px;
  color: #d4d4d4;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.def-title :deep(.katex) {
  font-size: 1em;
}
</style>
