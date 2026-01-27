<template>
  <div class="note-editor-page">
    <div class="header">
      <NuxtLink to="/" class="back-link">← Back</NuxtLink>
      <h2>{{ note?.title || 'Loading...' }}</h2>
    </div>

    <div class="editor-layout">
      <div class="editor-section">
        <div class="pane latex-pane">
          <div class="pane-header">LaTeX Editor</div>
          <LatexEditor v-model="latexSource" />
        </div>
        <div class="pane preview-pane">
          <div class="pane-header">Preview</div>
          <PreviewPane :source="latexSource" />
        </div>
      </div>

      <div class="lean-section">
        <LeanPanel :lean-code="leanCode" :imports="leanImports" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { getNote, updateNote } from '~/utils/api'
import { debounce } from '~/utils/debounce'
import type { Note } from '~/types/api'
import LatexEditor from '~/components/editor/LatexEditor.vue'
import PreviewPane from '~/components/editor/PreviewPane.vue'
import LeanPanel from '~/components/lean/LeanPanel.vue'

const route = useRoute()
const noteId = route.params.id as string

const note = ref<Note | null>(null)
const latexSource = ref('')
const leanCode = ref('')
const leanImports = ref<string[]>([])

const loadNote = async () => {
  try {
    note.value = await getNote(noteId)
    latexSource.value = note.value.latex_source
  } catch (error) {
    console.error('Failed to load note:', error)
  }
}

const debouncedUpdate = debounce(async (source: string) => {
  try {
    await updateNote(noteId, source)
  } catch (error) {
    console.error('Failed to update note:', error)
  }
}, 1000)

watch(latexSource, (newSource) => {
  debouncedUpdate(newSource)
})

onMounted(() => {
  loadNote()
})
</script>

<style scoped>
.note-editor-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #2d2d2d;
  color: #d4d4d4;
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

.editor-layout {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-section {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  overflow: hidden;
}

.pane {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-right: 1px solid #3e3e42;
}

.pane:last-child {
  border-right: none;
}

.pane-header {
  padding: 8px 16px;
  background: #252526;
  border-bottom: 1px solid #3e3e42;
  font-size: 12px;
  font-weight: 500;
  color: #cccccc;
}

.lean-section {
  height: 300px;
  border-top: 1px solid #3e3e42;
}
</style>
