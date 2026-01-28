<template>
  <div class="file-tree">
    <div class="tree-header">
      <span class="title">Files</span>
      <div class="actions">
        <button class="action-btn" title="New File" @click="showNewFileInput = true">+</button>
        <button class="action-btn" title="New Folder" @click="showNewFolderInput = true">📁</button>
        <button class="action-btn" title="Refresh" @click="$emit('refresh')">↻</button>
      </div>
    </div>

    <div v-if="showNewFileInput" class="new-item-input">
      <input
        ref="newFileInputRef"
        v-model="newFileName"
        type="text"
        placeholder="filename.tex"
        @keyup.enter="createNewFile"
        @keyup.escape="cancelNewFile"
        @blur="cancelNewFile"
      />
    </div>

    <div v-if="showNewFolderInput" class="new-item-input">
      <input
        ref="newFolderInputRef"
        v-model="newFolderName"
        type="text"
        placeholder="folder name"
        @keyup.enter="createNewFolder"
        @keyup.escape="cancelNewFolder"
        @blur="cancelNewFolder"
      />
    </div>

    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="tree.length === 0" class="empty">No files found</div>
    <div v-else class="tree-content">
      <FileTreeNode
        v-for="node in tree"
        :key="node.path"
        :node="node"
        :depth="0"
        :selected-path="selectedPath"
        @select="$emit('select', $event)"
        @context-menu="handleContextMenu"
      />
    </div>

    <div
      v-if="contextMenu"
      class="context-menu"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
    >
      <button @click="handleRename">Rename</button>
      <button class="danger" @click="handleDelete">Delete</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import type { FileNode } from '~/types/api'
import FileTreeNode from './FileTreeNode.vue'

const props = defineProps<{
  tree: FileNode[]
  selectedPath: string | null
  loading: boolean
}>()

const emit = defineEmits<{
  select: [path: string]
  refresh: []
  createFile: [path: string]
  createFolder: [path: string]
  rename: [oldPath: string, newPath: string]
  delete: [path: string, type: 'file' | 'directory']
}>()

const showNewFileInput = ref(false)
const showNewFolderInput = ref(false)
const newFileName = ref('')
const newFolderName = ref('')
const newFileInputRef = ref<HTMLInputElement | null>(null)
const newFolderInputRef = ref<HTMLInputElement | null>(null)

const contextMenu = ref<{ node: FileNode; x: number; y: number } | null>(null)

const createNewFile = () => {
  if (newFileName.value.trim()) {
    let path = newFileName.value.trim()
    if (!path.endsWith('.tex')) {
      path += '.tex'
    }
    emit('createFile', path)
  }
  cancelNewFile()
}

const cancelNewFile = () => {
  showNewFileInput.value = false
  newFileName.value = ''
}

const createNewFolder = () => {
  if (newFolderName.value.trim()) {
    emit('createFolder', newFolderName.value.trim())
  }
  cancelNewFolder()
}

const cancelNewFolder = () => {
  showNewFolderInput.value = false
  newFolderName.value = ''
}

const handleContextMenu = (event: { node: FileNode; x: number; y: number }) => {
  contextMenu.value = event
}

const closeContextMenu = () => {
  contextMenu.value = null
}

const handleRename = () => {
  if (!contextMenu.value) return
  const node = contextMenu.value.node
  const newName = prompt('New name:', node.name)
  if (newName && newName !== node.name) {
    const parentPath = node.path.split('/').slice(0, -1).join('/')
    const newPath = parentPath ? `${parentPath}/${newName}` : newName
    emit('rename', node.path, newPath)
  }
  closeContextMenu()
}

const handleDelete = () => {
  if (!contextMenu.value) return
  const node = contextMenu.value.node
  if (confirm(`Delete ${node.name}?`)) {
    emit('delete', node.path, node.type)
  }
  closeContextMenu()
}

// Focus input when shown
const focusNewFileInput = async () => {
  await nextTick()
  newFileInputRef.value?.focus()
}

const focusNewFolderInput = async () => {
  await nextTick()
  newFolderInputRef.value?.focus()
}

// Watch for showNewFileInput/showNewFolderInput changes
import { watch } from 'vue'
watch(showNewFileInput, (val) => val && focusNewFileInput())
watch(showNewFolderInput, (val) => val && focusNewFolderInput())

// Close context menu on click outside
const handleGlobalClick = () => closeContextMenu()
onMounted(() => document.addEventListener('click', handleGlobalClick))
onUnmounted(() => document.removeEventListener('click', handleGlobalClick))
</script>

<style scoped>
.file-tree {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #1e1e1e;
  position: relative;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #3e3e42;
}

.title {
  font-size: 12px;
  font-weight: 600;
  color: #bbbbbb;
  text-transform: uppercase;
}

.actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  padding: 2px 6px;
  background: transparent;
  border: none;
  color: #cccccc;
  cursor: pointer;
  font-size: 14px;
  border-radius: 3px;
}

.action-btn:hover {
  background: #3e3e42;
}

.new-item-input {
  padding: 4px 8px;
  border-bottom: 1px solid #3e3e42;
}

.new-item-input input {
  width: 100%;
  padding: 4px 8px;
  background: #3c3c3c;
  border: 1px solid #007acc;
  border-radius: 3px;
  color: #d4d4d4;
  font-size: 13px;
  outline: none;
}

.loading,
.empty {
  padding: 16px;
  color: #808080;
  font-size: 13px;
  text-align: center;
}

.tree-content {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
}

.context-menu {
  position: fixed;
  background: #252526;
  border: 1px solid #3e3e42;
  border-radius: 4px;
  padding: 4px 0;
  min-width: 120px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  z-index: 1000;
}

.context-menu button {
  display: block;
  width: 100%;
  padding: 6px 12px;
  background: none;
  border: none;
  color: #d4d4d4;
  font-size: 13px;
  text-align: left;
  cursor: pointer;
}

.context-menu button:hover {
  background: #094771;
}

.context-menu button.danger:hover {
  background: #c42b1c;
}
</style>
