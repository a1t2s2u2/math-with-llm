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
      <ThemeToggle />
    </div>

    <div class="main-layout">
      <ResizablePanes
        :horizontal="true"
        :initial-sizes="[12, 68, 20]"
        :collapsible="true"
        :collapsible-panes="[0, 2]"
      >
        <template #pane-0>
          <div class="sidebar">
            <ResizablePanes :horizontal="false" :initial-sizes="[50, 50]">
              <template #pane-0>
                <FileTree
                  :tree="fileTree"
                  :selected-path="currentPath"
                  :loading="treeLoading"
                  :workspace-path="workspacePath"
                  @select="handleFileSelect"
                  @refresh="loadTree"
                  @create-file="handleCreateFile"
                  @create-folder="handleCreateFolder"
                  @rename="handleRename"
                  @delete="handleDelete"
                  @change-workspace="handleChangeWorkspace"
                  @move="handleRename"
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
                      @select-block="handleSelectBlock"
                      @deselect-block="handleDeselectBlock"
                    />
                    <GitPanel
                      v-if="activeTab === 'git'"
                      ref="gitPanelRef"
                      @show-diff="diffView = $event"
                      @file-discarded="handleFileDiscarded"
                    />
                  </div>
                </div>
              </template>
            </ResizablePanes>
          </div>
        </template>

        <template #pane-1>
          <GitDiffView
            v-if="diffView"
            :path="diffView.path"
            :staged="diffView.staged"
            @close="diffView = null"
          />

          <div v-else-if="!currentFile" class="empty-state">
            <div class="empty-content">
              <h2>No file selected</h2>
              <p>Select a file from the tree or create a new one to get started.</p>
            </div>
          </div>

          <ResizablePanes v-else :horizontal="true" :initial-sizes="[50, 50]">
            <template #pane-0>
              <div class="pane latex-pane">
                <div class="pane-header">
                  {{ currentFile.name }}{{ isDirty ? ' *' : '' }}
                  <button class="handwriting-btn" @click="openHandwriting">✏️ 手書き入力</button>
                </div>
                <LatexEditor
                  ref="editorRef"
                  :model-value="localContent"
                  :original-content="originalContent"
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

        <template #pane-2>
          <div class="ai-section">
            <AIAssistantPanel
              ref="aiPanelRef"
              @send="handleAIChat"
              @generate-skeleton="handleGenerateSkeleton"
            />
          </div>
        </template>
      </ResizablePanes>
    </div>

    <HandwritingModal ref="handwritingModalRef" @insert="handleInsertLatex" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFile } from '~/composables/useFile'
import {
  getFileTree,
  getWorkspace,
  changeWorkspace,
  createFile,
  createFolder,
  renameFile,
  deleteFile,
  deleteFolder,
  chatStreamApi,
  getGitOriginal,
  getGitStatus,
  generateSkeleton
} from '~/utils/api'
import type { FileNode, Block, AIContext } from '~/types/api'
import { BLOCK_TYPE_LABELS } from '~/utils/constants'

import LatexEditor from '~/components/editor/LatexEditor.vue'
import PreviewPane from '~/components/editor/PreviewPane.vue'
import AIAssistantPanel from '~/components/ai/AIAssistantPanel.vue'
import OutlinePanel from '~/components/outline/OutlinePanel.vue'
import ResizablePanes from '~/components/ui/ResizablePanes.vue'
import FileTree from '~/components/files/FileTree.vue'
import GitPanel from '~/components/git/GitPanel.vue'
import GitDiffView from '~/components/git/GitDiffView.vue'
import ThemeToggle from '~/components/ui/ThemeToggle.vue'
import HandwritingModal from '~/components/handwriting/HandwritingModal.vue'

// ファイルツリー状態
const fileTree = ref<FileNode[]>([])
const treeLoading = ref(false)
const workspacePath = ref('')

// 現在のファイル状態
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

// エディタ状態
const activeTab = ref('outline')
const scrollSyncEnabled = ref(true)
const editorScrollLine = ref(1)
const previewScrollLine = ref(1)
const editorRef = ref<InstanceType<typeof LatexEditor> | null>(null)
const aiPanelRef = ref<InstanceType<typeof AIAssistantPanel> | null>(null)
const handwritingModalRef = ref<InstanceType<typeof HandwritingModal> | null>(null)

const gitPanelRef = ref<InstanceType<typeof GitPanel> | null>(null)
const diffView = ref<{ path: string; staged: boolean } | null>(null)
const originalContent = ref<string | null>(null)

const tabs = [
  { id: 'outline', label: 'Outline' },
  { id: 'git', label: 'Git' }
]

// currentFileからの算出プロパティ
const blocks = computed<Block[]>(() => currentFile.value?.blocks || [])

// ファイルツリー読み込み
const loadTree = async () => {
  treeLoading.value = true
  fileTree.value = await getFileTree()
  treeLoading.value = false
}

// ワークスペース変更
const handleChangeWorkspace = async (path: string) => {
  try {
    treeLoading.value = true
    clearFile()
    fileTree.value = await changeWorkspace(path)
    workspacePath.value = path
  } catch {
    alert(`Failed to open workspace: ${path}`)
  } finally {
    treeLoading.value = false
  }
}

// ファイル選択
const handleFileSelect = async (path: string) => {
  await loadFile(path)
  await fetchOriginalContent(path)
  if (currentFile.value && aiPanelRef.value) {
    aiPanelRef.value.setContext({
      type: 'block',
      label: currentFile.value.name,
      content: currentFile.value.content
    })
  }
}

const fetchOriginalContent = async (path: string) => {
  const status = await getGitStatus()
  if (!status.is_repo) {
    originalContent.value = null
    return
  }
  const result = await getGitOriginal(path)
  originalContent.value = result.content
}

// ファイル操作
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

// Git破棄ハンドラ
const handleFileDiscarded = async (path: string) => {
  if (currentPath.value === path) {
    await loadFile(path)
    await fetchOriginalContent(path)
  }
}

// エディタイベント
const handleEditorScroll = (line: number) => {
  editorScrollLine.value = line
}

const handlePreviewScroll = (line: number) => {
  previewScrollLine.value = line
}

const handleJump = (position: number) => {
  editorRef.value?.scrollToPosition(position)
}

// 保存ハンドラ
const handleSave = async () => {
  await saveFile()
  gitPanelRef.value?.refresh()
}

// AIアシスト
const handleSelectBlock = (block: Block) => {
  if (!aiPanelRef.value) return
  const typeLabel = BLOCK_TYPE_LABELS[block.type] || block.type
  const label = block.title ? `${typeLabel}: ${block.title}` : typeLabel
  aiPanelRef.value.setContext({
    type: 'block',
    label,
    content: block.latex_fragment,
    blockType: block.type,
    blockId: block.id
  })
}

const handleDeselectBlock = () => {
  if (!aiPanelRef.value) return
  if (currentFile.value) {
    aiPanelRef.value.setContext({
      type: 'block',
      label: currentFile.value.name,
      content: currentFile.value.content
    })
  } else {
    aiPanelRef.value.clearContext()
  }
}

const handleGenerateSkeleton = async () => {
  if (!aiPanelRef.value || !currentPath.value) return
  const ctx = aiPanelRef.value.getContext()
  if (!ctx?.blockId) return
  aiPanelRef.value.setSkeletonLoading(true)
  try {
    const result = await generateSkeleton(currentPath.value, ctx.blockId)
    aiPanelRef.value.setSkeleton(result.cards)
  } catch (e) {
    console.error('Failed to generate skeleton:', e)
    aiPanelRef.value.addAssistantMessage('スケルトン生成に失敗しました。もう一度お試しください。')
  } finally {
    aiPanelRef.value.setSkeletonLoading(false)
  }
}

const handleAIChat = async (
  message: string,
  context: AIContext | null,
  history: import('~/types/api').ChatMessage[]
) => {
  if (!aiPanelRef.value) return
  aiPanelRef.value.startAssistantStream()
  try {
    const options =
      context?.blockId && currentPath.value
        ? {
            filePath: currentPath.value,
            blockId: context.blockId,
            onReferences: (refs: import('~/types/api').BlockReference[]) => {
              aiPanelRef.value?.setLastAssistantReferences(refs)
            }
          }
        : undefined

    await chatStreamApi(
      message,
      context?.type || null,
      context?.content || null,
      (chunk) => {
        aiPanelRef.value?.appendToLastAssistant(chunk)
      },
      { ...options, history }
    )
  } catch (e) {
    console.error('Failed to chat:', e)
    aiPanelRef.value.addAssistantMessage('エラーが発生しました。もう一度お試しください。')
  } finally {
    aiPanelRef.value.finishAssistantStream()
  }
}

// 手書き入力
const openHandwriting = () => {
  handwritingModalRef.value?.open()
}

const handleInsertLatex = (latex: string) => {
  editorRef.value?.insertTextAtCursor(latex)
  setLocalContent(localContent.value)
}

onMounted(async () => {
  try {
    const ws = await getWorkspace()
    workspacePath.value = ws.path
    await loadTree()
  } catch (e) {
    console.error('Failed to initialize workspace:', e)
    // エラーが発生してもUIは表示する
    treeLoading.value = false
  }
})
</script>

<style scoped>
.workspace-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-secondary);
  color: var(--color-text);
  overflow: hidden;
}

.header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 16px;
  background: var(--color-bg-header);
  border-bottom: 1px solid var(--color-border);
}

.header h1 {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--color-text-secondary);
}

.header-spacer {
  flex: 1;
}

.sync-toggle {
  padding: 4px 12px;
  font-size: var(--font-size-sm);
  background: var(--color-border);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.sync-toggle:hover {
  background: var(--color-bg-hover);
}

.sync-toggle.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-bg-main);
}

.main-layout {
  flex: 1;
  overflow: hidden;
}

.sidebar {
  height: 100%;
  background: var(--color-bg-main);
  border-right: 1px solid var(--color-border);
}

.outline-section {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-main);
  border-top: 1px solid var(--color-border);
}

.tabs {
  display: flex;
  background: var(--color-bg-header);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.tab {
  flex: 1;
  padding: 6px 4px;
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
  cursor: pointer;
  border-bottom: 2px solid transparent;
}

.tab:hover {
  color: var(--color-text);
}

.tab.active {
  color: var(--color-text);
  border-bottom-color: var(--color-primary);
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
  background: var(--color-bg-main);
}

.empty-content {
  text-align: center;
  color: var(--color-text-muted);
}

.empty-content h2 {
  font-size: var(--font-size-lg);
  font-weight: 500;
  margin-bottom: 8px;
}

.empty-content p {
  font-size: var(--font-size-base);
}

.pane {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.pane-header {
  padding: 8px 16px;
  background: var(--color-bg-header);
  border-bottom: 1px solid var(--color-border);
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.handwriting-btn {
  margin-left: auto;
  padding: 4px 12px;
  font-size: var(--font-size-xs);
  background: var(--color-bg-main);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  color: var(--color-text);
  cursor: pointer;
  transition: all 0.2s;
}

.handwriting-btn:hover {
  background: var(--color-bg-hover);
  border-color: var(--color-primary);
}

.latex-pane,
.preview-pane {
  border-right: 1px solid var(--color-border);
}

.ai-section {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
