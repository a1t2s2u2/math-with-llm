<template>
  <div class="tree-node">
    <div
      class="node-row"
      :class="{ selected: isSelected, directory: node.type === 'directory' }"
      :style="{ paddingLeft: `${depth * 16 + 8}px` }"
      @click="handleClick"
      @contextmenu.prevent="handleContextMenu"
    >
      <span v-if="node.type === 'directory'" class="icon folder-icon">
        {{ expanded ? '▼' : '▶' }}
      </span>
      <span v-else class="icon file-icon">📄</span>
      <span class="name">{{ node.name }}</span>
    </div>

    <div v-if="node.type === 'directory' && expanded && node.children" class="children">
      <FileTreeNode
        v-for="child in node.children"
        :key="child.path"
        :node="child"
        :depth="depth + 1"
        :selected-path="selectedPath"
        @select="$emit('select', $event)"
        @context-menu="$emit('context-menu', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { FileNode } from '~/types/api'

const props = defineProps<{
  node: FileNode
  depth: number
  selectedPath: string | null
}>()

const emit = defineEmits<{
  select: [path: string]
  'context-menu': [event: { node: FileNode; x: number; y: number }]
}>()

const expanded = ref(props.depth === 0)

const isSelected = computed(() => props.selectedPath === props.node.path)

const handleClick = () => {
  if (props.node.type === 'directory') {
    expanded.value = !expanded.value
  } else {
    emit('select', props.node.path)
  }
}

const handleContextMenu = (event: MouseEvent) => {
  emit('context-menu', {
    node: props.node,
    x: event.clientX,
    y: event.clientY
  })
}
</script>

<style scoped>
.tree-node {
  user-select: none;
}

.node-row {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  cursor: pointer;
  border-radius: 3px;
  transition: background 0.1s;
}

.node-row:hover {
  background: #2d2d2d;
}

.node-row.selected {
  background: #094771;
}

.node-row.directory {
  font-weight: 500;
}

.icon {
  font-size: 12px;
  width: 16px;
  text-align: center;
  flex-shrink: 0;
}

.folder-icon {
  color: #808080;
  font-size: 10px;
}

.file-icon {
  font-size: 14px;
}

.name {
  font-size: 13px;
  color: #d4d4d4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.children {
  /* Children are indented via paddingLeft on node-row */
}
</style>
