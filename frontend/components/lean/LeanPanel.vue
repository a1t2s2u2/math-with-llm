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
  background: #1e1e1e;
  border-top: 1px solid #3e3e3e;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #252526;
  border-bottom: 1px solid #3e3e3e;
}

.panel-header h3 {
  margin: 0;
  font-size: 14px;
  color: #d4d4d4;
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
  background: #1e1e1e;
  color: #d4d4d4;
}

.result-section {
  padding: 12px 16px;
  background: #252526;
  border-top: 1px solid #3e3e3e;
  max-height: 200px;
  overflow-y: auto;
  color: #d4d4d4;
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
  background: #5a1d1d;
  border-left: 3px solid #f14c4c;
  color: #f48771;
}

.diagnostic.warning {
  background: #4d4a2a;
  border-left: 3px solid #ffc107;
  color: #f0e68c;
}

.logs {
  font-size: 11px;
  background: #1e1e1e;
  padding: 8px;
  overflow-x: auto;
  color: #d4d4d4;
}
</style>
