<template>
  <div class="lean-panel">
    <div class="panel-header">
      <h3>Lean Code</h3>
      <button @click="checkCode" :disabled="checking" class="check-button">
        {{ checking ? 'Checking...' : 'Check' }}
      </button>
    </div>

    <textarea
      v-model="code"
      class="lean-editor"
      placeholder="Lean code will appear here..."
    />

    <div v-if="result" class="result-section">
      <h4>Result: <span :class="result.status">{{ result.status }}</span></h4>
      <div v-if="result.diagnostics.length > 0" class="diagnostics">
        <div
          v-for="(diag, i) in result.diagnostics"
          :key="i"
          :class="['diagnostic', diag.severity]"
        >
          <strong>Line {{ diag.line }}, Col {{ diag.column }}:</strong>
          {{ diag.message }}
        </div>
      </div>
      <pre v-if="result.logs" class="logs">{{ result.logs }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { checkLean } from '~/utils/api'
import type { LeanCheckResult } from '~/types/api'

const props = defineProps<{
  leanCode: string
  imports: string[]
}>()

const code = ref(props.leanCode)
const checking = ref(false)
const result = ref<LeanCheckResult | null>(null)

const checkCode = async () => {
  checking.value = true
  try {
    result.value = await checkLean(code.value, props.imports)
  } catch (error) {
    console.error('Lean check failed:', error)
  } finally {
    checking.value = false
  }
}
</script>

<style scoped>
.lean-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f5f5;
  border-top: 1px solid #ccc;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #ccc;
}

.panel-header h3 {
  margin: 0;
  font-size: 14px;
}

.check-button {
  padding: 6px 12px;
  background: #007acc;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.check-button:hover:not(:disabled) {
  background: #005a9e;
}

.check-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.lean-editor {
  flex: 1;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  padding: 12px;
  border: none;
  resize: none;
  outline: none;
}

.result-section {
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid #ccc;
  max-height: 200px;
  overflow-y: auto;
}

.result-section h4 {
  margin: 0 0 8px 0;
  font-size: 13px;
}

.result-section .success {
  color: #28a745;
}

.result-section .failure {
  color: #dc3545;
}

.result-section .timeout {
  color: #ffc107;
}

.diagnostics {
  margin-bottom: 8px;
}

.diagnostic {
  padding: 6px;
  margin: 4px 0;
  border-radius: 3px;
  font-size: 12px;
}

.diagnostic.error {
  background: #ffe6e6;
  border-left: 3px solid #dc3545;
}

.diagnostic.warning {
  background: #fff3cd;
  border-left: 3px solid #ffc107;
}

.logs {
  font-size: 11px;
  background: #f8f8f8;
  padding: 8px;
  overflow-x: auto;
}
</style>
