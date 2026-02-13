<template>
  <div v-if="show" class="workspace-picker-overlay" @click="handleOverlayClick">
    <div class="workspace-picker" @click.stop>
      <div class="picker-header">
        <h3>Select Workspace Folder</h3>
        <button class="close-button" @click="close">×</button>
      </div>

      <div class="current-path">
        <span class="path-label">Current:</span>
        <span class="path-value">{{ currentPath }}</span>
      </div>

      <div class="directory-list">
        <div v-if="loading" class="loading">Loading...</div>
        <template v-else>
          <div v-if="currentPath !== '/'" class="directory-item parent" @click="goToParent">
            <span class="folder-icon">📁</span>
            <span class="folder-name">..</span>
          </div>
          <div
            v-for="dir in directories"
            :key="dir"
            class="directory-item"
            @click="navigateToDirectory(dir)"
          >
            <span class="folder-icon">📁</span>
            <span class="folder-name">{{ dir }}</span>
          </div>
          <div v-if="directories.length === 0" class="empty">No subdirectories</div>
        </template>
      </div>

      <div class="picker-actions">
        <button class="cancel-button" @click="close">Cancel</button>
        <button class="select-button" @click="selectCurrent">Select This Folder</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  close: []
  select: [path: string]
}>()

const currentPath = ref('/')
const directories = ref<string[]>([])
const loading = ref(false)

const API_BASE = '/api'

const loadDirectory = async (path: string | null = null) => {
  loading.value = true
  try {
    const url = path
      ? `${API_BASE}/files/workspace/browse?path=${encodeURIComponent(path)}`
      : `${API_BASE}/files/workspace/browse`
    const response = await fetch(url)
    if (!response.ok) throw new Error('Failed to load directory')
    const data = await response.json()
    currentPath.value = data.current
    directories.value = data.dirs
  } catch (error) {
    console.error('Failed to load directory:', error)
    alert('Failed to load directory')
  } finally {
    loading.value = false
  }
}

const navigateToDirectory = (dir: string) => {
  const newPath = currentPath.value === '/' ? `/${dir}` : `${currentPath.value}/${dir}`
  loadDirectory(newPath)
}

const goToParent = () => {
  const parts = currentPath.value.split('/').filter((p) => p)
  if (parts.length === 0) return
  parts.pop()
  const parentPath = parts.length === 0 ? '/' : `/${parts.join('/')}`
  loadDirectory(parentPath)
}

const selectCurrent = () => {
  emit('select', currentPath.value)
  close()
}

const close = () => {
  emit('close')
}

const handleOverlayClick = () => {
  close()
}

watch(
  () => props.show,
  (newShow) => {
    if (newShow) {
      loadDirectory()
    }
  }
)
</script>

<style scoped>
.workspace-picker-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.workspace-picker {
  width: 600px;
  max-width: 90vw;
  max-height: 80vh;
  background: var(--color-bg-main);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
}

.picker-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
}

.close-button {
  width: 28px;
  height: 28px;
  padding: 0;
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  font-size: 24px;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background: var(--color-bg-hover);
  color: var(--color-text);
}

.current-path {
  padding: 12px 20px;
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
  font-size: 13px;
  display: flex;
  gap: 8px;
}

.path-label {
  color: var(--color-text-muted);
  font-weight: 500;
}

.path-value {
  color: var(--color-text);
  font-family: monospace;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.directory-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  min-height: 300px;
}

.loading {
  padding: 40px;
  text-align: center;
  color: var(--color-text-muted);
}

.directory-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.15s;
}

.directory-item:hover {
  background: var(--color-bg-hover);
}

.directory-item.parent {
  color: var(--color-text-muted);
  font-weight: 500;
}

.folder-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.folder-name {
  font-size: 14px;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty {
  padding: 40px;
  text-align: center;
  color: var(--color-text-muted);
  font-size: 14px;
}

.picker-actions {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--color-border);
  justify-content: flex-end;
}

.cancel-button,
.select-button {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.cancel-button {
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.cancel-button:hover {
  background: var(--color-bg-hover);
}

.select-button {
  background: var(--color-primary);
  color: var(--color-bg-main);
  font-weight: 500;
}

.select-button:hover {
  background: var(--color-primary-hover);
}
</style>
