<template>
  <div class="ai-panel">
    <div class="panel-header">
      <h3>AI Assistant</h3>
      <button v-if="messages.length > 0" class="clear-button" @click="clearAll">Clear</button>
    </div>

    <div class="messages-container" ref="messagesRef">
      <template v-if="skeleton">
        <div v-for="(card, i) in skeleton" :key="i" class="skeleton-card">
          <div class="skeleton-strategy">{{ card.strategy }}</div>
          <div class="skeleton-description" v-html="renderMath(card.description)" />
          <div v-if="card.required_lemmas.length > 0" class="skeleton-section">
            <div class="skeleton-section-title">必要な補題</div>
            <ul>
              <li v-for="(lemma, j) in card.required_lemmas" :key="j" v-html="renderMath(lemma)" />
            </ul>
          </div>
          <div v-if="card.assumptions_to_check.length > 0" class="skeleton-section">
            <div class="skeleton-section-title">確認事項</div>
            <ul>
              <li
                v-for="(item, j) in card.assumptions_to_check"
                :key="j"
                v-html="renderMath(item)"
              />
            </ul>
          </div>
        </div>
      </template>

      <template v-else>
        <div v-if="messages.length === 0 && !context" class="empty-state">
          <p>Outlineでブロックをクリック、またはエディタでテキストを選択してください</p>
        </div>

        <div v-for="(msg, i) in messages" :key="i" class="message" :class="msg.role">
          <div class="message-content" v-html="renderMath(msg.content)" />
          <button class="copy-button" @click="copyMessage(msg.content)" title="コピー">
            <svg v-if="copiedIndex === i" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="currentColor">
              <path
                d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"
              />
            </svg>
          </button>
        </div>

        <div v-if="loading" class="message assistant loading-message">
          <span class="spinner" />
          考え中...
        </div>
      </template>

      <div v-if="skeletonLoading" class="message assistant loading-message">
        <span class="spinner" />
        スケルトン生成中...
      </div>
    </div>

    <div v-if="context" class="context-bar">
      <div class="context-label">コンテキスト:</div>
      <div class="context-content">{{ contextLabel }}</div>
      <button
        v-if="isProvableBlock"
        class="skeleton-button"
        :disabled="skeletonLoading"
        @click="emit('generateSkeleton')"
      >
        Skeleton
      </button>
      <button class="context-clear" @click="clearContext">×</button>
    </div>

    <div class="input-area">
      <textarea
        v-model="inputText"
        placeholder="質問を入力... (Enterで送信)"
        @keydown="handleKeydown"
        :disabled="loading || streaming"
      />
      <button class="send-button" @click="sendMessage" :disabled="!canSend">送信</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useMathRender } from '~/composables/useMathRender'
import type { AIContext, SkeletonCard } from '~/types/api'
import { PROVABLE_BLOCK_TYPES } from '~/utils/constants'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const emit = defineEmits<{
  send: [message: string, context: AIContext | null]
  generateSkeleton: []
}>()

const messages = ref<Message[]>([])
const inputText = ref('')
const loading = ref(false)
const context = ref<AIContext | null>(null)
const messagesRef = ref<HTMLElement | null>(null)
const copiedIndex = ref<number | null>(null)
const streaming = ref(false)
const skeleton = ref<SkeletonCard[] | null>(null)
const skeletonLoading = ref(false)

const { renderMath } = useMathRender()

const contextLabel = computed(() => {
  if (!context.value) return ''
  if (context.value.type === 'block') return context.value.label
  return `選択: "${context.value.content.slice(0, 30)}${context.value.content.length > 30 ? '...' : ''}"`
})

const canSend = computed(() => inputText.value.trim() && !loading.value && !streaming.value)

const isProvableBlock = computed(
  () =>
    context.value?.type === 'block' &&
    context.value.blockType !== undefined &&
    PROVABLE_BLOCK_TYPES.has(context.value.blockType)
)

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter') {
    if (e.metaKey || e.ctrlKey) {
      // Cmd/Ctrl+Enter: 改行挿入
      e.preventDefault()
      const textarea = e.target as HTMLTextAreaElement
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      inputText.value = inputText.value.substring(0, start) + '\n' + inputText.value.substring(end)
      nextTick(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 1
      })
    } else if (!e.shiftKey) {
      // Enter（修飾キーなし）: 送信
      e.preventDefault()
      sendMessage()
    }
    // Shift+Enter: デフォルト動作（改行）
  }
}

const sendMessage = () => {
  if (!canSend.value) return
  const text = inputText.value.trim()
  inputText.value = ''

  messages.value.push({ role: 'user', content: text })
  scrollToBottom()

  emit('send', text, context.value)
}

const addAssistantMessage = (content: string) => {
  messages.value.push({ role: 'assistant', content })
  scrollToBottom()
}

const startAssistantStream = (): number => {
  streaming.value = true
  messages.value.push({ role: 'assistant', content: '' })
  scrollToBottom()
  return messages.value.length - 1
}

const appendToLastAssistant = (chunk: string) => {
  const last = messages.value[messages.value.length - 1]
  if (last?.role === 'assistant') {
    last.content += chunk
    scrollToBottom()
  }
}

const finishAssistantStream = () => {
  streaming.value = false
}

const setLoading = (value: boolean) => {
  loading.value = value
}

const setContext = (ctx: AIContext) => {
  context.value = ctx
}

const clearContext = () => {
  context.value = null
  skeleton.value = null
  skeletonLoading.value = false
}

const clearAll = () => {
  messages.value = []
  context.value = null
  skeleton.value = null
  skeletonLoading.value = false
}

const setSkeleton = (cards: SkeletonCard[]) => {
  skeleton.value = cards
  scrollToBottom()
}

const setSkeletonLoading = (value: boolean) => {
  skeletonLoading.value = value
}

const getContext = () => context.value

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

const copyMessage = async (content: string) => {
  await navigator.clipboard.writeText(content)
  const index = messages.value.findIndex((m) => m.content === content)
  copiedIndex.value = index
  setTimeout(() => {
    copiedIndex.value = null
  }, 1500)
}

defineExpose({
  addAssistantMessage,
  startAssistantStream,
  appendToLastAssistant,
  finishAssistantStream,
  setLoading,
  setContext,
  clearContext,
  clearAll,
  setSkeleton,
  setSkeletonLoading,
  getContext
})
</script>

<style scoped>
.ai-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg-main);
  border-left: 1px solid var(--color-border);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: var(--color-bg-header);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.panel-header h3 {
  margin: 0;
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.clear-button {
  padding: 2px 8px;
  font-size: 11px;
  background: var(--color-border);
  color: var(--color-text-secondary);
  border: none;
  border-radius: 3px;
  cursor: pointer;
}

.clear-button:hover {
  background: var(--color-bg-hover);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.empty-state {
  color: var(--color-text-dimmed);
  font-size: 12px;
  text-align: center;
  padding: 24px;
}

.empty-state p {
  margin: 0;
}

.message {
  position: relative;
  margin-bottom: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.5;
}

.copy-button {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 24px;
  height: 24px;
  padding: 4px;
  background: var(--color-border);
  border: none;
  border-radius: 3px;
  color: var(--color-text-dimmed);
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.15s;
}

.copy-button svg {
  width: 16px;
  height: 16px;
  display: block;
}

.message:hover .copy-button {
  opacity: 1;
}

.copy-button:hover {
  background: var(--color-bg-hover);
  color: var(--color-text);
}

.message.user {
  background: var(--color-primary);
  color: #ffffff;
  margin-left: 24px;
}

.message.assistant {
  background: var(--color-bg-secondary);
  color: var(--color-text);
  margin-right: 24px;
  border: 1px solid var(--color-border);
}

.message-content {
  white-space: pre-wrap;
  word-break: break-word;
}

.message-content :deep(.katex) {
  font-size: 1em;
}

.message-content :deep(.katex-display) {
  overflow-x: auto;
  overflow-y: hidden;
  padding: 4px 0;
  margin: 8px 0;
}

.message-content :deep(.katex-display > .katex) {
  white-space: nowrap;
}

.loading-message {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text-dimmed);
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.context-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border);
  font-size: 11px;
}

.context-label {
  color: var(--color-text-dimmed);
  flex-shrink: 0;
}

.context-content {
  flex: 1;
  color: var(--color-accent);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.skeleton-button {
  padding: 2px 8px;
  font-size: 11px;
  background: var(--color-primary);
  color: #ffffff;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  flex-shrink: 0;
}

.skeleton-button:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.skeleton-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.context-clear {
  padding: 2px 6px;
  background: none;
  border: none;
  color: var(--color-text-dimmed);
  cursor: pointer;
  font-size: 14px;
}

.context-clear:hover {
  color: var(--color-text);
}

.skeleton-card {
  margin-bottom: 12px;
  padding: 12px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.5;
}

.skeleton-strategy {
  font-weight: 600;
  color: var(--color-accent);
  margin-bottom: 6px;
}

.skeleton-description {
  color: var(--color-text);
  margin-bottom: 8px;
  white-space: pre-wrap;
  word-break: break-word;
}

.skeleton-section {
  margin-top: 8px;
}

.skeleton-section-title {
  font-size: 11px;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.skeleton-section ul {
  margin: 0;
  padding-left: 18px;
}

.skeleton-section li {
  color: var(--color-text);
  margin-bottom: 2px;
}

.input-area {
  display: flex;
  gap: 8px;
  padding: 12px;
  background: var(--color-bg-header);
  border-top: 1px solid var(--color-border);
}

.input-area textarea {
  flex: 1;
  min-height: 36px;
  max-height: 100px;
  padding: 8px 12px;
  background: var(--color-bg-main);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  color: var(--color-text);
  font-size: 13px;
  font-family: inherit;
  resize: none;
  outline: none;
}

.input-area textarea:focus {
  border-color: var(--color-primary);
}

.input-area textarea::placeholder {
  color: var(--color-text-dimmed);
}

.send-button {
  padding: 8px 16px;
  background: var(--color-primary);
  color: #ffffff;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.send-button:disabled {
  background: var(--color-border);
  color: var(--color-text-dimmed);
  cursor: not-allowed;
}
</style>
