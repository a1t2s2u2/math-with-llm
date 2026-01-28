<template>
  <div class="note-editor-page">
    <div class="header">
      <NuxtLink to="/" class="back-link">← Back</NuxtLink>
      <h2>{{ note?.title || 'Loading...' }}</h2>
    </div>

    <div class="main-layout">
      <ResizablePanes :horizontal="true" :initial-sizes="[15, 85]">
        <template #pane-0>
          <div class="sidebar">
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
            <div class="sidebar-content">
              <OutlinePanel
                v-if="activeTab === 'outline'"
                :blocks="blocks"
                @generate-skeleton="handleGenerateSkeleton"
                @generate-lean="handleGenerateLean"
              />
              <DefinitionLedger v-if="activeTab === 'definitions'" :definitions="definitions" />
              <SymbolTable v-if="activeTab === 'symbols'" :symbols="symbols" />
              <TodoList v-if="activeTab === 'todos'" :todos="todos" />
            </div>
          </div>
        </template>

        <template #pane-1>
          <ResizablePanes :horizontal="false" :initial-sizes="[70, 30]">
            <template #pane-0>
              <ResizablePanes :horizontal="true" :initial-sizes="[50, 50]">
                <template #pane-0>
                  <div class="pane latex-pane">
                    <div class="pane-header">LaTeX Editor</div>
                    <LatexEditor v-model="latexSource" />
                  </div>
                </template>
                <template #pane-1>
                  <div class="pane preview-pane">
                    <div class="pane-header">Preview</div>
                    <PreviewPane :rendered-html="note?.rendered_html || ''" />
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
import { ref, onMounted, watch } from 'vue'
import { useNote } from '~/composables/useNote'
import { useLatex } from '~/composables/useLatex'
import { useLean } from '~/composables/useLean'
import { useAssist } from '~/composables/useAssist'
import LatexEditor from '~/components/editor/LatexEditor.vue'
import PreviewPane from '~/components/editor/PreviewPane.vue'
import LeanPanel from '~/components/lean/LeanPanel.vue'
import OutlinePanel from '~/components/outline/OutlinePanel.vue'
import DefinitionLedger from '~/components/outline/DefinitionLedger.vue'
import SymbolTable from '~/components/outline/SymbolTable.vue'
import TodoList from '~/components/outline/TodoList.vue'
import SkeletonModal from '~/components/ui/SkeletonModal.vue'
import ResizablePanes from '~/components/ui/ResizablePanes.vue'

const route = useRoute()
const noteId = route.params.id as string

const { note, load, updateSource } = useNote(noteId)
const { blocks, symbols, todos, definitions } = useLatex(note)
const { code: leanCode, imports: leanImports, setCode } = useLean()
const { skeletonCards, loadingSkeleton, requestSkeleton, requestLean } = useAssist(noteId)

const latexSource = ref('')
const activeTab = ref('outline')
const showSkeletonModal = ref(false)

const tabs = [
  { id: 'outline', label: 'Outline' },
  { id: 'definitions', label: 'Definitions' },
  { id: 'symbols', label: 'Symbols' },
  { id: 'todos', label: 'TODOs' }
]

watch(latexSource, (newSource) => {
  updateSource(newSource)
})

watch(note, (newNote) => {
  if (newNote) {
    latexSource.value = newNote.latex_source
  }
})

const handleGenerateSkeleton = async (blockId: string) => {
  showSkeletonModal.value = true
  await requestSkeleton(blockId)
}

const handleGenerateLean = async (blockId: string) => {
  const result = await requestLean(blockId)
  setCode(result.lean_code, result.imports)
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.note-editor-page {
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
  padding: 12px 16px;
  background: #252526;
  border-bottom: 1px solid #3e3e42;
}

.back-link {
  color: #007acc;
  text-decoration: none;
  font-size: 14px;
}

.back-link:hover {
  text-decoration: underline;
}

.header h2 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.main-layout {
  flex: 1;
  overflow: hidden;
}

.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #1e1e1e;
  border-right: 1px solid #3e3e42;
}

.tabs {
  display: flex;
  background: #252526;
  border-bottom: 1px solid #3e3e42;
}

.tab {
  flex: 1;
  padding: 8px 4px;
  background: none;
  border: none;
  color: #cccccc;
  font-size: 11px;
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

.sidebar-content {
  flex: 1;
  overflow: hidden;
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
