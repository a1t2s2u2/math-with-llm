<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const emit = defineEmits<{
  export: [blob: Blob]
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const isDrawing = ref(false)
const tool = ref<'pen' | 'eraser'>('pen')
const lineWidth = ref(3)

let ctx: CanvasRenderingContext2D | null = null
const undoStack = ref<ImageData[]>([])
const redoStack = ref<ImageData[]>([])

function saveSnapshot() {
  if (!ctx || !canvasRef.value) return
  undoStack.value.push(ctx.getImageData(0, 0, canvasRef.value.width, canvasRef.value.height))
  redoStack.value = []
}

function undo() {
  if (!ctx || !canvasRef.value || undoStack.value.length === 0) return
  redoStack.value.push(ctx.getImageData(0, 0, canvasRef.value.width, canvasRef.value.height))
  ctx.putImageData(undoStack.value.pop()!, 0, 0)
}

function redo() {
  if (!ctx || !canvasRef.value || redoStack.value.length === 0) return
  undoStack.value.push(ctx.getImageData(0, 0, canvasRef.value.width, canvasRef.value.height))
  ctx.putImageData(redoStack.value.pop()!, 0, 0)
}

const eraserRadius = computed(() => lineWidth.value * 4)
const eraserCursor = computed(() => {
  const r = eraserRadius.value
  const size = r * 2
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='${size}' height='${size}'><circle cx='${r}' cy='${r}' r='${r - 1}' fill='none' stroke='%23888' stroke-width='1.5'/></svg>`
  return `url("data:image/svg+xml,${svg}") ${r} ${r}, crosshair`
})

onMounted(() => {
  if (!canvasRef.value) return

  ctx = canvasRef.value.getContext('2d')
  if (!ctx) return

  const canvas = canvasRef.value
  const dpr = window.devicePixelRatio || 1
  const rect = canvas.getBoundingClientRect()

  canvas.width = rect.width * dpr
  canvas.height = rect.height * dpr

  ctx.scale(dpr, dpr)
  canvas.style.width = `${rect.width}px`
  canvas.style.height = `${rect.height}px`

  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
})

function getCoordinates(event: PointerEvent): { x: number; y: number } | null {
  if (!canvasRef.value) return null
  const rect = canvasRef.value.getBoundingClientRect()
  return {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
}

function handlePointerDown(event: PointerEvent) {
  if (!ctx) return
  const coords = getCoordinates(event)
  if (!coords) return

  saveSnapshot()
  isDrawing.value = true
  ctx.beginPath()
  ctx.moveTo(coords.x, coords.y)

  if (tool.value === 'pen') {
    ctx.strokeStyle = '#000000'
    ctx.lineWidth = lineWidth.value
  } else {
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = lineWidth.value * 8
  }
}

function handlePointerMove(event: PointerEvent) {
  if (!isDrawing.value || !ctx) return
  const coords = getCoordinates(event)
  if (!coords) return

  ctx.lineTo(coords.x, coords.y)
  ctx.stroke()
}

function handlePointerUp() {
  isDrawing.value = false
}

function handlePointerCancel() {
  isDrawing.value = false
}

function clear() {
  if (!ctx || !canvasRef.value) return
  saveSnapshot()
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height)
}

function exportImage() {
  if (!canvasRef.value) return

  canvasRef.value.toBlob((blob) => {
    if (blob) {
      emit('export', blob)
    }
  }, 'image/png')
}

defineExpose({ exportImage, clear })
</script>

<template>
  <div class="handwriting-canvas">
    <div class="toolbar">
      <button :class="{ active: tool === 'pen' }" class="tool-btn" @click="tool = 'pen'">
        ✏️ ペン
      </button>
      <button :class="{ active: tool === 'eraser' }" class="tool-btn" @click="tool = 'eraser'">
        🧹 消しゴム
      </button>
      <button class="tool-btn" :disabled="undoStack.length === 0" @click="undo">↩ 戻る</button>
      <button class="tool-btn" :disabled="redoStack.length === 0" @click="redo">↪ 進む</button>
      <button class="tool-btn" @click="clear">🗑️ クリア</button>
    </div>
    <canvas
      ref="canvasRef"
      class="canvas"
      :style="tool === 'eraser' ? { cursor: eraserCursor } : {}"
      @pointerdown="handlePointerDown"
      @pointermove="handlePointerMove"
      @pointerup="handlePointerUp"
      @pointercancel="handlePointerCancel"
    />
  </div>
</template>

<style scoped>
.handwriting-canvas {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
}

.toolbar {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.tool-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #ccc;
  border-radius: 0.25rem;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.tool-btn:hover {
  background: #f0f0f0;
}

.tool-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.tool-btn.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.canvas {
  flex: 1;
  border: 2px solid #ccc;
  border-radius: 0.25rem;
  cursor: crosshair;
  touch-action: none;
  background: white;
}
</style>
