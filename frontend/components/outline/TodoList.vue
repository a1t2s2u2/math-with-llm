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
  padding: 8px;
  background: #1e1e1e;
  height: 100%;
  overflow-y: auto;
}

h3 {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 8px;
  padding: 0 8px;
  color: #cccccc;
}

.empty {
  color: #858585;
  font-size: 12px;
  padding: 8px;
}

.todo-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.todo-item {
  padding: 6px 8px;
  background: #ffc10722;
  border-left: 3px solid #ffc107;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
}

.todo-item:hover {
  background: #ffc10744;
}

.todo-line {
  font-size: 10px;
  font-weight: 600;
  color: #ffd966;
  margin-right: 8px;
}

.todo-content {
  font-size: 12px;
  color: #d4d4d4;
}
</style>
