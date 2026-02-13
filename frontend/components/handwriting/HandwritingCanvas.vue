<script setup lang="ts">
import { ref, onMounted } from 'vue'

const emit = defineEmits<{
  export: [blob: Blob]
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const isDrawing = ref(false)
const tool = ref<'pen' | 'eraser'>('pen')
const lineWidth = ref(3)

let ctx: CanvasRenderingContext2D | null = null

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

  isDrawing.value = true
  ctx.beginPath()
  ctx.moveTo(coords.x, coords.y)

  if (tool.value === 'pen') {
    ctx.strokeStyle = '#000000'
    ctx.lineWidth = lineWidth.value
  } else {
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = lineWidth.value * 3
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
      <button :class="{ active: tool === 'pen' }" @click="tool = 'pen'" class="tool-btn">
        ✏️ ペン
      </button>
      <button :class="{ active: tool === 'eraser' }" @click="tool = 'eraser'" class="tool-btn">
        🧹 消しゴム
      </button>
      <button @click="clear" class="tool-btn">🗑️ クリア</button>
    </div>
    <canvas
      ref="canvasRef"
      class="canvas"
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
