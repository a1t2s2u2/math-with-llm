<template>
  <div class="latex-editor">
    <ClientOnly>
      <VueMonacoEditor
        v-model:value="localSource"
        language="latex"
        theme="vs-dark"
        :options="editorOptions"
        @change="onInput"
        @mount="onEditorMount"
      />
      <template #fallback>
        <div class="editor-loading">Loading editor...</div>
      </template>
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, shallowRef } from 'vue'
import { VueMonacoEditor } from '@guolao/vue-monaco-editor'
import { debounce } from '~/utils/debounce'
import type * as Monaco from 'monaco-editor'

const props = defineProps<{
  modelValue: string
  scrollLine?: number
  syncEnabled?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  scroll: [lineNumber: number]
}>()

const localSource = ref(props.modelValue)
const editorRef = shallowRef<Monaco.editor.IStandaloneCodeEditor | null>(null)
const isScrollingProgrammatically = ref(false)

const editorOptions: Monaco.editor.IStandaloneEditorConstructionOptions = {
  fontSize: 14,
  fontFamily: "'Monaco', 'Courier New', monospace",
  minimap: { enabled: false },
  lineNumbers: 'on',
  wordWrap: 'on',
  automaticLayout: true,
  scrollBeyondLastLine: false,
  padding: { top: 16 }
}

const debouncedEmit = debounce((value: string) => {
  emit('update:modelValue', value)
}, 500)

const onInput = (value: string | undefined) => {
  if (value !== undefined) {
    debouncedEmit(value)
  }
}

// Scroll to specific line
const scrollToLine = (lineNumber: number) => {
  if (!editorRef.value) return
  isScrollingProgrammatically.value = true
  editorRef.value.revealLineInCenter(lineNumber)
  setTimeout(() => {
    isScrollingProgrammatically.value = false
  }, 50)
}

const onEditorMount = (editor: Monaco.editor.IStandaloneCodeEditor, monaco: typeof Monaco) => {
  editorRef.value = editor

  // Emit current visible line number on scroll
  editor.onDidScrollChange(() => {
    if (isScrollingProgrammatically.value || !props.syncEnabled) return
    const visibleRanges = editor.getVisibleRanges()
    if (visibleRanges.length > 0) {
      const topLine = visibleRanges[0].startLineNumber
      emit('scroll', topLine)
    }
  })

  // Register LaTeX language if not already registered
  if (!monaco.languages.getLanguages().some((lang) => lang.id === 'latex')) {
    monaco.languages.register({ id: 'latex' })

    monaco.languages.setMonarchTokensProvider('latex', {
      tokenizer: {
        root: [
          // Comments
          [/%.*$/, 'comment'],

          // Math mode (display)
          [/\$\$/, { token: 'string', next: '@mathDisplay' }],
          [/\\\[/, { token: 'string', next: '@mathDisplayBracket' }],

          // Math mode (inline)
          [/\$/, { token: 'string', next: '@mathInline' }],
          [/\\\(/, { token: 'string', next: '@mathInlineParen' }],

          // Environments
          [/\\begin\{([^}]+)\}/, 'keyword'],
          [/\\end\{([^}]+)\}/, 'keyword'],

          // Commands
          [/\\[a-zA-Z@]+\*?/, 'keyword'],

          // Braces
          [/[{}]/, 'delimiter.bracket'],
          [/\[|\]/, 'delimiter.square']
        ],
        mathInline: [
          [/\$/, { token: 'string', next: '@pop' }],
          [/\\./, 'string'],
          [/[^$\\]+/, 'string']
        ],
        mathInlineParen: [
          [/\\\)/, { token: 'string', next: '@pop' }],
          [/\\./, 'string'],
          [/[^\\]+/, 'string']
        ],
        mathDisplay: [
          [/\$\$/, { token: 'string', next: '@pop' }],
          [/\\./, 'string'],
          [/[^$\\]+/, 'string']
        ],
        mathDisplayBracket: [
          [/\\\]/, { token: 'string', next: '@pop' }],
          [/\\./, 'string'],
          [/[^\\]+/, 'string']
        ]
      }
    })
  }
}

watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue !== localSource.value) {
      localSource.value = newValue
    }
  }
)

watch(
  () => props.scrollLine,
  (line) => {
    if (props.syncEnabled && line !== undefined && line > 0) {
      scrollToLine(line)
    }
  }
)
</script>

<style scoped>
.latex-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.editor-loading {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1e1e1e;
  color: #808080;
  font-family: 'Monaco', 'Courier New', monospace;
}
</style>
