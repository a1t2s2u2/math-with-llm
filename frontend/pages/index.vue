<template>
  <div class="workspace-page">
    <div class="header">
      <h1>Math with LLM</h1>
      <div class="header-spacer" />
      <button
        v-if="currentFile"
        :class="['sync-toggle', { active: scrollSyncEnabled }]"
        @click="scrollSyncEnabled = !scrollSyncEnabled"
      >
        {{ scrollSyncEnabled ? 'Sync ON' : 'Sync OFF' }}
      </button>
    </div>

    <div class="main-layout">
      <ResizablePanes :horizontal="true" :initial-sizes="[20, 80]">
        <template #pane-0>
          <div class="sidebar">
            <ResizablePanes :horizontal="false" :initial-sizes="[50, 50]">
              <template #pane-0>
                <FileTree
                  :tree="fileTree"
                  :selected-path="currentPath"
                  :loading="treeLoading"
                  @select="handleFileSelect"
                  @refresh="loadTree"
                  @create-file="handleCreateFile"
                  @create-folder="handleCreateFolder"
                  @rename="handleRename"
                  @delete="handleDelete"
                />
              </template>

              <template #pane-1>
                <div class="outline-section">
                  <div class="tabs">
                    <button
                      v-for="tab in tabs"
                      :key="tab.id"
                      :class="['tab', { active: activeTab === tab.id }]"
                      @click="activeTab = tab.id"
                    >
                      {{ tab.label }}
                    </button>
                  </div>
                  <div class="outline-content">
                    <OutlinePanel
                      v-if="activeTab === 'outline'"
                      :blocks="blocks"
                      @jump="handleJump"
                      @generate-skeleton="handleGenerateSkeleton"
                      @generate-lean="handleGenerateLean"
                    />
                    <DefinitionLedger
                      v-if="activeTab === 'definitions'"
                      :definitions="definitions"
                      @jump="handleJump"
                    />
                    <TodoList v-if="activeTab === 'todos'" :todos="todos" />
                  </div>
                </div>
              </template>
            </ResizablePanes>
          </div>
        </template>

        <template #pane-1>
          <div v-if="!currentFile" class="empty-state">
            <div class="empty-content">
              <h2>No file selected</h2>
              <p>Select a file from the tree or create a new one to get started.</p>
            </div>
          </div>

          <template v-else>
            <ResizablePanes :horizontal="false" :initial-sizes="[70, 30]">
              <template #pane-0>
                <ResizablePanes :horizontal="true" :initial-sizes="[50, 50]">
                  <template #pane-0>
                    <div class="pane latex-pane">
                      <div class="pane-header">{{ currentFile.name }}{{ isDirty ? ' *' : '' }}</div>
                      <LatexEditor
                        ref="editorRef"
                        :model-value="localContent"
                        :scroll-line="previewScrollLine"
                        :sync-enabled="scrollSyncEnabled"
                        @update:model-value="setLocalContent"
                        @scroll="handleEditorScroll"
                        @save="handleSave"
                      />
                    </div>
                  </template>
                  <template #pane-1>
                    <div class="pane preview-pane">
                      <div class="pane-header">Preview</div>
                      <PreviewPane
                        :rendered-html="currentFile.rendered_html"
                        :scroll-line="editorScrollLine"
                        :sync-enabled="scrollSyncEnabled"
                        @scroll="handlePreviewScroll"
                      />
                    </div>
                  </template>
                </ResizablePanes>
              </template>

              <template #pane-1>
                <div class="lean-section">
                  <LeanPanel
                    :lean-code="leanCode"
                    :imports="leanImports"
                    @generate-for-block="handleGenerateLean"
                  />
                </div>
              </template>
            </ResizablePanes>
          </template>
        </template>
      </ResizablePanes>
    </div>

    <SkeletonModal
      :show="showSkeletonModal"
      :cards="skeletonCards"
      :loading="loadingSkeleton"
      @close="showSkeletonModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFile } from '~/composables/useFile'
import { useLean } from '~/composables/useLean'
import {
  getFileTree,
  createFile,
  createFolder,
  renameFile,
  deleteFile,
  deleteFolder,
  generateFileSkeletonApi,
  generateFileLeanApi
} from '~/utils/api'
import type { FileNode, Block, Todo, SkeletonCard } from '~/types/api'

import LatexEditor from '~/components/editor/LatexEditor.vue'
import PreviewPane from '~/components/editor/PreviewPane.vue'
import LeanPanel from '~/components/lean/LeanPanel.vue'
import OutlinePanel from '~/components/outline/OutlinePanel.vue'
import DefinitionLedger from '~/components/outline/DefinitionLedger.vue'
import TodoList from '~/components/outline/TodoList.vue'
import SkeletonModal from '~/components/ui/SkeletonModal.vue'
import ResizablePanes from '~/components/ui/ResizablePanes.vue'
import FileTree from '~/components/files/FileTree.vue'

// File tree state
const fileTree = ref<FileNode[]>([])
const treeLoading = ref(false)

// Current file state
const {
  file: currentFile,
  currentPath,
  localContent,
  isDirty,
  load: loadFile,
  setLocalContent,
  save: saveFile,
  clear: clearFile
} = useFile()

// Lean state
const { code: leanCode, imports: leanImports } = useLean()

// Editor state
const activeTab = ref('outline')
const scrollSyncEnabled = ref(true)
const editorScrollLine = ref(1)
const previewScrollLine = ref(1)
const editorRef = ref<InstanceType<typeof LatexEditor> | null>(null)

// Skeleton modal state
const showSkeletonModal = ref(false)
const skeletonCards = ref<SkeletonCard[]>([])
const loadingSkeleton = ref(false)

const tabs = [
  { id: 'outline', label: 'Outline' },
  { id: 'definitions', label: 'Defs' },
  { id: 'todos', label: 'TODOs' }
]

// Computed from currentFile
const blocks = computed<Block[]>(() => currentFile.value?.blocks || [])
const todos = computed<Todo[]>(() => currentFile.value?.todos || [])
const definitions = computed(() => blocks.value.filter((b) => b.type === 'definition'))

// Load file tree
const loadTree = async () => {
  treeLoading.value = true
  fileTree.value = await getFileTree()
  treeLoading.value = false
}

// File selection
const handleFileSelect = async (path: string) => {
  await loadFile(path)
}

// File operations
const handleCreateFile = async (path: string) => {
  await createFile(path)
  await loadTree()
  await handleFileSelect(path)
}

const handleCreateFolder = async (path: string) => {
  await createFolder(path)
  await loadTree()
}

const handleRename = async (oldPath: string, newPath: string) => {
  await renameFile(oldPath, newPath)
  await loadTree()
  if (currentPath.value === oldPath) {
    await handleFileSelect(newPath)
  }
}

const handleDelete = async (path: string, type: 'file' | 'directory') => {
  if (type === 'file') {
    await deleteFile(path)
  } else {
    await deleteFolder(path)
  }
  await loadTree()
  if (currentPath.value === path) {
    clearFile()
  }
}

// Editor events
const handleEditorScroll = (line: number) => {
  editorScrollLine.value = line
}

const handlePreviewScroll = (line: number) => {
  previewScrollLine.value = line
}

const handleJump = (position: number) => {
  editorRef.value?.scrollToPosition(position)
}

// Save handler
const handleSave = async () => {
  await saveFile()
}

// LLM assist
const handleGenerateSkeleton = async (blockId: string) => {
  if (!currentPath.value) return
  showSkeletonModal.value = true
  loadingSkeleton.value = true
  skeletonCards.value = []
  const result = await generateFileSkeletonApi(currentPath.value, blockId)
  skeletonCards.value = result.cards
  loadingSkeleton.value = false
}

const handleGenerateLean = async (blockId: string) => {
  if (!currentPath.value) return
  const result = await generateFileLeanApi(currentPath.value, blockId)
  // TODO: setCode(result.lean_code, result.imports)
  console.log('Generated Lean:', result)
}

onMounted(() => {
  loadTree()
})
</script>

<style scoped>
.workspace-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #2d2d2d;
  color: #d4d4d4;
  overflow: hidden;
}

.header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 16px;
  background: #252526;
  border-bottom: 1px solid #3e3e42;
}

.header h1 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #cccccc;
}

.header-spacer {
  flex: 1;
}

.sync-toggle {
  padding: 4px 12px;
  font-size: 12px;
  background: #3e3e42;
  border: 1px solid #5a5a5a;
  border-radius: 4px;
  color: #808080;
  cursor: pointer;
  transition: all 0.2s;
}

.sync-toggle:hover {
  background: #4e4e52;
}

.sync-toggle.active {
  background: #007acc;
  border-color: #007acc;
  color: #ffffff;
}

.main-layout {
  flex: 1;
  overflow: hidden;
}

.sidebar {
  height: 100%;
  background: #1e1e1e;
  border-right: 1px solid #3e3e42;
}

.outline-section {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #1e1e1e;
  border-top: 1px solid #3e3e42;
}

.tabs {
  display: flex;
  background: #252526;
  border-bottom: 1px solid #3e3e42;
  flex-shrink: 0;
}

.tab {
  flex: 1;
  padding: 6px 4px;
  background: none;
  border: none;
  color: #cccccc;
  font-size: 10px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
}

.tab:hover {
  color: #ffffff;
}

.tab.active {
  color: #ffffff;
  border-bottom-color: #007acc;
}

.outline-content {
  flex: 1;
  overflow: hidden;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1e1e1e;
}

.empty-content {
  text-align: center;
  color: #808080;
}

.empty-content h2 {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 8px;
}

.empty-content p {
  font-size: 14px;
}

.pane {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.pane-header {
  padding: 8px 16px;
  background: #252526;
  border-bottom: 1px solid #3e3e42;
  font-size: 12px;
  font-weight: 500;
  color: #cccccc;
  flex-shrink: 0;
}

.latex-pane,
.preview-pane {
  border-right: 1px solid #3e3e42;
}

.lean-section {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-top: 1px solid #3e3e42;
}
</style>
