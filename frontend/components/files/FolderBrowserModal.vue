<template>
  <div class="modal-overlay" @click.self="$emit('cancel')">
    <div class="modal-dialog">
      <div class="modal-header">
        <span class="modal-title">Open Folder</span>
        <button class="close-btn" @click="$emit('cancel')">×</button>
      </div>

      <div class="path-input-row">
        <input
          v-model="pathInput"
          class="path-input"
          type="text"
          placeholder="/path/to/folder"
          @keyup.enter="navigateTo(pathInput)"
        />
        <button class="go-btn" @click="navigateTo(pathInput)">Go</button>
      </div>

      <div class="dir-list">
        <div v-if="loading" class="loading">Loading...</div>
        <template v-else>
          <div class="dir-item parent" @click="navigateUp">
            <span class="dir-icon">..</span>
          </div>
          <div
            v-for="dir in dirs"
            :key="dir"
            class="dir-item"
            @click="navigateTo(`${currentPath}/${dir}`)"
          >
            <span class="dir-icon">📁</span>
            <span class="dir-name">{{ dir }}</span>
          </div>
          <div v-if="dirs.length === 0" class="empty">No subdirectories</div>
        </template>
      </div>

      <div class="modal-footer">
        <button class="btn cancel-btn" @click="$emit('cancel')">Cancel</button>
        <button class="btn open-btn" @click="$emit('select', currentPath)">Open</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { browseDirectory } from '~/utils/api'

const props = defineProps<{
  initialPath?: string
}>()

defineEmits<{
  select: [path: string]
  cancel: []
}>()

const currentPath = ref('')
const pathInput = ref('')
const dirs = ref<string[]>([])
const loading = ref(false)

const browse = async (path?: string) => {
  loading.value = true
  const result = await browseDirectory(path)
  currentPath.value = result.current
  pathInput.value = result.current
  dirs.value = result.dirs
  loading.value = false
}

const navigateTo = (path: string) => {
  browse(path)
}

const navigateUp = () => {
  const parent = currentPath.value.split('/').slice(0, -1).join('/') || '/'
  browse(parent)
}

onMounted(() => {
  browse(props.initialPath || undefined)
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-dialog {
  background: #252526;
  border: 1px solid #3e3e42;
  border-radius: 8px;
  width: 500px;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #3e3e42;
}

.modal-title {
  font-size: 14px;
  font-weight: 600;
  color: #d4d4d4;
}

.close-btn {
  background: none;
  border: none;
  color: #808080;
  font-size: 18px;
  cursor: pointer;
  padding: 0 4px;
}

.close-btn:hover {
  color: #d4d4d4;
}

.path-input-row {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid #3e3e42;
}

.path-input {
  flex: 1;
  padding: 6px 10px;
  background: #3c3c3c;
  border: 1px solid #5a5a5a;
  border-radius: 4px;
  color: #d4d4d4;
  font-size: 13px;
  outline: none;
}

.path-input:focus {
  border-color: #007acc;
}

.go-btn {
  padding: 6px 14px;
  background: #3e3e42;
  border: 1px solid #5a5a5a;
  border-radius: 4px;
  color: #d4d4d4;
  cursor: pointer;
  font-size: 13px;
}

.go-btn:hover {
  background: #4e4e52;
}

.dir-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 0;
  min-height: 200px;
  max-height: 400px;
}

.dir-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  cursor: pointer;
  color: #d4d4d4;
  font-size: 13px;
}

.dir-item:hover {
  background: #2d2d2d;
}

.dir-item.parent {
  color: #808080;
}

.dir-icon {
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}

.dir-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.loading,
.empty {
  padding: 16px;
  color: #808080;
  font-size: 13px;
  text-align: center;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #3e3e42;
}

.btn {
  padding: 6px 16px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid transparent;
}

.cancel-btn {
  background: #3e3e42;
  border-color: #5a5a5a;
  color: #d4d4d4;
}

.cancel-btn:hover {
  background: #4e4e52;
}

.open-btn {
  background: #007acc;
  color: #ffffff;
}

.open-btn:hover {
  background: #0098ff;
}
</style>
