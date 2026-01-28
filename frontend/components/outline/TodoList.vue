<template>
  <div class="todo-list">
    <h3>TODOs</h3>
    <div v-if="todos.length === 0" class="empty">No TODOs found</div>
    <div v-else class="todo-items">
      <div
        v-for="(todo, index) in todos"
        :key="index"
        class="todo-item"
        @click="$emit('jump', todo.line_number)"
      >
        <span class="todo-line">Line {{ todo.line_number }}</span>
        <span class="todo-content">{{ todo.content }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Todo } from '~/types/api'

defineProps<{
  todos: Todo[]
}>()

defineEmits<{
  jump: [lineNumber: number]
}>()
</script>

<style scoped>
.todo-list {
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

.todo-items {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.todo-item {
  padding: 10px 12px;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.todo-item:hover {
  background: #ffe69c;
}

.todo-line {
  font-size: 11px;
  font-weight: 600;
  color: #856404;
  margin-right: 8px;
}

.todo-content {
  font-size: 13px;
  color: #212529;
}
</style>
