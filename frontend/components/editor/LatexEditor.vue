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
import { buildLCSIndices, matchBySimilarity } from '~/utils/gitDiff'
import type * as Monaco from 'monaco-editor'

const props = defineProps<{
  modelValue: string
  originalContent?: string | null
  scrollLine?: number
  syncEnabled?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
  scroll: [lineNumber: number]
  save: []
}>()

const localSource = ref(props.modelValue)
const editorRef = shallowRef<Monaco.editor.IStandaloneCodeEditor | null>(null)
const isScrollingProgrammatically = ref(false)
const monacoInstance = shallowRef<typeof Monaco | null>(null)

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

// 指定行へスクロール
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
  monacoInstance.value = monaco

  // 保存コマンド登録 (Cmd+S / Ctrl+S)
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
    emit('save')
  })

  // スクロール時に表示中の行番号をemit
  editor.onDidScrollChange(() => {
    if (isScrollingProgrammatically.value || !props.syncEnabled) return
    const visibleRanges = editor.getVisibleRanges()
    if (visibleRanges.length > 0) {
      const topLine = visibleRanges[0].startLineNumber
      emit('scroll', topLine)
    }
  })

  // LaTeX言語が未登録なら登録
  if (!monaco.languages.getLanguages().some((lang) => lang.id === 'latex')) {
    monaco.languages.register({ id: 'latex' })

    monaco.languages.setMonarchTokensProvider('latex', {
      tokenizer: {
        root: [
          // コメント
          [/%.*$/, 'comment'],

          // 数式モード（ディスプレイ）
          [/\$\$/, { token: 'string', next: '@mathDisplay' }],
          [/\\\[/, { token: 'string', next: '@mathDisplayBracket' }],

          // 数式モード（インライン）
          [/\$/, { token: 'string', next: '@mathInline' }],
          [/\\\(/, { token: 'string', next: '@mathInlineParen' }],

          // 環境
          [/\\begin\{([^}]+)\}/, 'keyword'],
          [/\\end\{([^}]+)\}/, 'keyword'],

          // コマンド
          [/\\[a-zA-Z@]+\*?/, 'keyword'],

          // 括弧
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

// Gitガターデコレーション
let decorationIds: string[] = []

function computeGutterDecorations(monaco: typeof Monaco) {
  const editor = editorRef.value
  if (!editor) return

  const original = props.originalContent
  if (original == null) {
    decorationIds = editor.deltaDecorations(decorationIds, [])
    return
  }

  const oldLines = original.split('\n')
  const newLines = localSource.value.split('\n')
  const decorations: Monaco.editor.IModelDeltaDecoration[] = []

  // LCS でアンカー（完全一致行）のインデックスペアを取得
  const anchors: [number, number][] = [
    [-1, -1],
    ...buildLCSIndices(oldLines, newLines),
    [oldLines.length, newLines.length]
  ]

  for (let a = 0; a < anchors.length - 1; a++) {
    const [prevOi, prevNi] = anchors[a]
    const [nextOi, nextNi] = anchors[a + 1]

    const oldGap = oldLines.slice(prevOi + 1, nextOi)
    const newGap = newLines.slice(prevNi + 1, nextNi)
    const newGapStart = prevNi + 1

    if (oldGap.length === 0 && newGap.length === 0) continue

    if (oldGap.length === 0) {
      // 純粋な追加
      for (let k = 0; k < newGap.length; k++) {
        decorations.push({
          range: new monaco.Range(newGapStart + k + 1, 1, newGapStart + k + 1, 1),
          options: { isWholeLine: true, linesDecorationsClassName: 'git-added-line' }
        })
      }
    } else if (newGap.length === 0) {
      // 純粋な削除
      const lineNum = nextNi > 0 ? nextNi : 1
      decorations.push({
        range: new monaco.Range(lineNum, 1, lineNum, 1),
        options: { isWholeLine: false, linesDecorationsClassName: 'git-deleted-line' }
      })
    } else {
      // 混合: 類似度ベースで old→new をマッチング
      const modifiedNewIndices = matchBySimilarity(oldGap, newGap)
      for (let k = 0; k < newGap.length; k++) {
        const cls = modifiedNewIndices.has(k) ? 'git-modified-line' : 'git-added-line'
        decorations.push({
          range: new monaco.Range(newGapStart + k + 1, 1, newGapStart + k + 1, 1),
          options: { isWholeLine: true, linesDecorationsClassName: cls }
        })
      }
      // マッチしなかった old 行 → 削除マーカー
      if (oldGap.length > modifiedNewIndices.size) {
        const lineNum = nextNi > 0 ? nextNi : 1
        decorations.push({
          range: new monaco.Range(lineNum, 1, lineNum, 1),
          options: { isWholeLine: false, linesDecorationsClassName: 'git-deleted-line' }
        })
      }
    }
  }

  decorationIds = editor.deltaDecorations(decorationIds, decorations)
}

watch([() => props.originalContent, () => localSource.value], () => {
  if (monacoInstance.value) computeGutterDecorations(monacoInstance.value)
})

// 指定文字位置へスクロールするメソッドを公開
const scrollToPosition = (charPos: number) => {
  if (!editorRef.value) return
  const model = editorRef.value.getModel()
  if (!model) return
  const position = model.getPositionAt(charPos)
  isScrollingProgrammatically.value = true
  editorRef.value.revealLineInCenter(position.lineNumber)
  editorRef.value.setPosition(position)
  editorRef.value.focus()
  setTimeout(() => {
    isScrollingProgrammatically.value = false
  }, 50)
}

defineExpose({ scrollToPosition })
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

<style>
.git-added-line {
  background: #2ea04370;
  width: 3px !important;
  margin-left: 3px;
}

.git-modified-line {
  background: #0078d4;
  width: 3px !important;
  margin-left: 3px;
}

.git-deleted-line {
  background: #f85149;
  width: 3px !important;
  margin-left: 3px;
  height: 3px !important;
  position: relative;
  top: 100%;
}
</style>
