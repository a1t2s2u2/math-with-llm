<template>
  <div class="ai-panel">
    <div class="panel-header">
      <h3>AI Assistant</h3>
      <button v-if="messages.length > 0" class="clear-button" @click="clearAll">Clear</button>
    </div>

    <div class="messages-container" ref="messagesRef">
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
    </div>

    <div v-if="context" class="context-bar">
      <div class="context-label">コンテキスト:</div>
      <div class="context-content">{{ contextLabel }}</div>
      <button class="context-clear" @click="clearContext">×</button>
    </div>

    <div class="input-area">
      <textarea
        v-model="inputText"
        placeholder="質問を入力... (Enterで送信)"
        @keydown="handleKeydown"
        :disabled="loading"
      />
      <button class="send-button" @click="sendMessage" :disabled="!canSend">送信</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useMathRender } from '~/composables/useMathRender'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface Context {
  type: 'block' | 'selection'
  label: string
  content: string
}

const emit = defineEmits<{
  send: [message: string, context: Context | null]
}>()

const messages = ref<Message[]>([])
const inputText = ref('')
const loading = ref(false)
const context = ref<Context | null>(null)
const messagesRef = ref<HTMLElement | null>(null)
const copiedIndex = ref<number | null>(null)

const { renderMath } = useMathRender()

const contextLabel = computed(() => {
  if (!context.value) return ''
  if (context.value.type === 'block') return context.value.label
  return `選択: "${context.value.content.slice(0, 30)}${context.value.content.length > 30 ? '...' : ''}"`
})

const canSend = computed(() => inputText.value.trim() && !loading.value)

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

const setLoading = (value: boolean) => {
  loading.value = value
}

const setContext = (ctx: Context) => {
  context.value = ctx
}

const clearContext = () => {
  context.value = null
}

const clearAll = () => {
  messages.value = []
  context.value = null
}

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
  setLoading,
  setContext,
  clearContext,
  clearAll
})
</script>

<style scoped>
.ai-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1e1e1e;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: #252526;
  border-bottom: 1px solid #3e3e42;
  flex-shrink: 0;
}

.panel-header h3 {
  margin: 0;
  font-size: 12px;
  font-weight: 500;
  color: #cccccc;
}

.clear-button {
  padding: 2px 8px;
  font-size: 11px;
  background: #3e3e42;
  color: #cccccc;
  border: none;
  border-radius: 3px;
  cursor: pointer;
}

.clear-button:hover {
  background: #4e4e52;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.empty-state {
  color: #858585;
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
  background: #3e3e42;
  border: none;
  border-radius: 3px;
  color: #858585;
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
  background: #4e4e52;
  color: #ffffff;
}

.message.user {
  background: #264f78;
  color: #ffffff;
  margin-left: 24px;
}

.message.assistant {
  background: #2d2d2d;
  color: #d4d4d4;
  margin-right: 24px;
  border: 1px solid #3e3e42;
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
  color: #858585;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #3e3e42;
  border-top-color: #007acc;
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
  background: #2d2d30;
  border-top: 1px solid #3e3e42;
  font-size: 11px;
}

.context-label {
  color: #858585;
  flex-shrink: 0;
}

.context-content {
  flex: 1;
  color: #4fc3f7;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.context-clear {
  padding: 2px 6px;
  background: none;
  border: none;
  color: #858585;
  cursor: pointer;
  font-size: 14px;
}

.context-clear:hover {
  color: #ffffff;
}

.input-area {
  display: flex;
  gap: 8px;
  padding: 12px;
  background: #252526;
  border-top: 1px solid #3e3e42;
}

.input-area textarea {
  flex: 1;
  min-height: 36px;
  max-height: 100px;
  padding: 8px 12px;
  background: #1e1e1e;
  border: 1px solid #3e3e42;
  border-radius: 4px;
  color: #d4d4d4;
  font-size: 13px;
  font-family: inherit;
  resize: none;
  outline: none;
}

.input-area textarea:focus {
  border-color: #007acc;
}

.input-area textarea::placeholder {
  color: #858585;
}

.send-button {
  padding: 8px 16px;
  background: #007acc;
  color: #ffffff;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  background: #005a9e;
}

.send-button:disabled {
  background: #3e3e42;
  color: #858585;
  cursor: not-allowed;
}
</style>
