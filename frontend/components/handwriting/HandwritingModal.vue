<script setup lang="ts">
import { ref } from 'vue'
import HandwritingCanvas from './HandwritingCanvas.vue'
import { convertHandwriting } from '~/utils/api'

const emit = defineEmits<{
  insert: [latex: string]
}>()

const isOpen = ref(false)
const canvasRef = ref<InstanceType<typeof HandwritingCanvas> | null>(null)
const isConverting = ref(false)
const error = ref('')
const pendingBlob = ref<Blob | null>(null)

function open() {
  isOpen.value = true
  error.value = ''
}

function close() {
  isOpen.value = false
  error.value = ''
  pendingBlob.value = null
}

function handleExport(blob: Blob) {
  pendingBlob.value = blob
}

async function handleConvert() {
  if (!canvasRef.value) return

  isConverting.value = true
  error.value = ''
  pendingBlob.value = null

  canvasRef.value.exportImage()

  await new Promise((resolve) => setTimeout(resolve, 100))

  if (!pendingBlob.value) {
    error.value = '画像のエクスポートに失敗しました'
    isConverting.value = false
    return
  }

  try {
    const result = await convertHandwriting(pendingBlob.value)
    emit('insert', result.latex)
    close()
    canvasRef.value.clear()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '変換に失敗しました'
  } finally {
    isConverting.value = false
  }
}

defineExpose({ open, close })
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click="close">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>手書き数式入力</h2>
        <button class="close-btn" @click="close">×</button>
      </div>

      <div class="modal-body">
        <HandwritingCanvas ref="canvasRef" @export="handleExport" />
      </div>

      <div class="modal-footer">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        <div class="button-group">
          <button class="btn btn-secondary" @click="close">キャンセル</button>
          <button :disabled="isConverting" class="btn btn-primary" @click="handleConvert">
            {{ isConverting ? '変換中...' : '変換' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 0.5rem;
  width: 90%;
  max-width: 800px;
  height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #000;
}

.modal-body {
  flex: 1;
  padding: 1.5rem;
  overflow: hidden;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.error-message {
  color: #dc3545;
  font-size: 0.875rem;
  padding: 0.5rem;
  background: #f8d7da;
  border-radius: 0.25rem;
}

.button-group {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #5a6268;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    height: 90vh;
  }
}
</style>
