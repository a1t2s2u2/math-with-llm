<template>
  <div class="ai-panel">
    <div class="panel-header">
      <h3>AI Assistant</h3>
      <button v-if="messages.length > 0" class="clear-button" @click="clearMessages">Clear</button>
    </div>

    <div class="messages-container">
      <div v-if="messages.length === 0" class="empty-state">
        Outlineパネルの💡ボタンで証明戦略を生成できます
      </div>

      <div v-for="(msg, i) in messages" :key="i" class="message" :class="msg.type">
        <div class="message-header">
          <span class="message-type">{{ msg.type === 'strategy' ? '証明戦略' : msg.type }}</span>
          <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
        </div>

        <div v-if="msg.type === 'strategy'" class="strategy-cards">
          <div v-for="(card, j) in msg.cards" :key="j" class="strategy-card">
            <h4>{{ card.strategy }}</h4>
            <p class="description" v-html="renderMath(card.description)" />

            <div v-if="card.required_lemmas.length > 0" class="section">
              <strong>必要な補題・定理:</strong>
              <ul>
                <li
                  v-for="(lemma, k) in card.required_lemmas"
                  :key="k"
                  v-html="renderMath(lemma)"
                />
              </ul>
            </div>

            <div v-if="card.assumptions_to_check.length > 0" class="section">
              <strong>確認事項:</strong>
              <ul>
                <li
                  v-for="(assumption, k) in card.assumptions_to_check"
                  :key="k"
                  v-html="renderMath(assumption)"
                />
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading">
        <span class="spinner" />
        生成中...
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { SkeletonCard } from '~/types/api'
import { useMathRender } from '~/composables/useMathRender'

interface Message {
  type: 'strategy'
  cards: SkeletonCard[]
  timestamp: Date
}

const messages = ref<Message[]>([])
const loading = ref(false)

const { renderMath } = useMathRender()

const addStrategyMessage = (cards: SkeletonCard[]) => {
  messages.value.push({
    type: 'strategy',
    cards,
    timestamp: new Date()
  })
}

const setLoading = (value: boolean) => {
  loading.value = value
}

const clearMessages = () => {
  messages.value = []
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })
}

defineExpose({
  addStrategyMessage,
  setLoading,
  clearMessages
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
  padding: 4px 8px;
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

.message {
  margin-bottom: 16px;
  padding: 12px;
  background: #252526;
  border-radius: 6px;
  border-left: 3px solid #007acc;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #3e3e42;
}

.message-type {
  font-size: 11px;
  font-weight: 600;
  color: #007acc;
  text-transform: uppercase;
}

.message-time {
  font-size: 10px;
  color: #858585;
}

.strategy-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.strategy-card {
  padding: 10px;
  background: #1e1e1e;
  border-radius: 4px;
  border: 1px solid #3e3e42;
}

.strategy-card h4 {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #4fc3f7;
}

.strategy-card .description {
  font-size: 12px;
  color: #d4d4d4;
  line-height: 1.5;
  margin: 0 0 8px 0;
}

.strategy-card .section {
  margin-top: 8px;
  font-size: 12px;
  color: #d4d4d4;
}

.strategy-card .section strong {
  color: #9cdcfe;
}

.strategy-card ul {
  margin: 4px 0 0 0;
  padding-left: 20px;
}

.strategy-card li {
  margin: 2px 0;
  line-height: 1.4;
}

.strategy-card :deep(.katex) {
  font-size: 1em;
}

.loading {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  color: #858585;
  font-size: 12px;
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
</style>
