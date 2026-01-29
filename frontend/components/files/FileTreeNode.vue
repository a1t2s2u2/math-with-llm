<template>
  <div class="tree-node">
    <div
      class="node-row"
      :class="{
        selected: isSelected,
        directory: node.type === 'directory',
        'drag-over': isDragOver
      }"
      :style="{ paddingLeft: `${depth * 16 + 8}px` }"
      :draggable="node.type === 'file'"
      @click="handleClick"
      @contextmenu.prevent="handleContextMenu"
      @dragstart="handleDragStart"
      @dragover.prevent="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
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
        @move="(oldPath, newPath) => $emit('move', oldPath, newPath)"
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
  move: [oldPath: string, newPath: string]
}>()

const expanded = ref(props.depth === 0)
const isDragOver = ref(false)

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

const handleDragStart = (event: DragEvent) => {
  event.dataTransfer?.setData('text/plain', props.node.path)
}

const handleDragOver = (event: DragEvent) => {
  if (!event.dataTransfer) return
  if (props.node.type === 'directory') {
    event.dataTransfer.dropEffect = 'move'
    isDragOver.value = true
  }
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const handleDrop = (event: DragEvent) => {
  isDragOver.value = false
  const sourcePath = event.dataTransfer?.getData('text/plain')
  if (!sourcePath || props.node.type !== 'directory') return
  if (sourcePath === props.node.path) return
  const fileName = sourcePath.split('/').pop()!
  const newPath = `${props.node.path}/${fileName}`
  if (sourcePath !== newPath) {
    emit('move', sourcePath, newPath)
  }
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

.node-row.drag-over {
  background: #2a4a2a;
  outline: 1px dashed #4ec94e;
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
