<template>
  <div class="resizable-panes" :class="{ horizontal, vertical: !horizontal }">
    <div v-for="(pane, index) in panes" :key="index" class="pane" :style="getPaneStyle(index)">
      <slot :name="`pane-${index}`" />
    </div>
    <div
      v-for="(_, index) in panes.slice(0, -1)"
      :key="`divider-${index}`"
      class="divider"
      :style="getDividerStyle(index)"
      @mousedown="startResize(index, $event)"
    >
      <div class="divider-handle" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  horizontal?: boolean
  initialSizes?: number[]
}>()

const panes = computed(() => {
  const count = props.initialSizes?.length || 2
  return Array(count).fill(0)
})

const sizes = ref<number[]>(props.initialSizes || [50, 50])

const resizing = ref(false)
const resizingIndex = ref(-1)
const startPos = ref(0)
const startSizes = ref<number[]>([])

const getPaneStyle = (index: number) => {
  const size = sizes.value[index]
  if (props.horizontal) {
    return {
      width: `${size}%`,
      height: '100%'
    }
  }
  return {
    width: '100%',
    height: `${size}%`
  }
}

const getDividerStyle = (index: number) => {
  const totalBefore = sizes.value.slice(0, index + 1).reduce((a, b) => a + b, 0)
  if (props.horizontal) {
    return {
      left: `${totalBefore}%`,
      top: '0',
      width: '4px',
      height: '100%',
      cursor: 'col-resize'
    }
  }
  return {
    left: '0',
    top: `${totalBefore}%`,
    width: '100%',
    height: '4px',
    cursor: 'row-resize'
  }
}

const startResize = (index: number, event: MouseEvent) => {
  event.preventDefault()
  resizing.value = true
  resizingIndex.value = index
  startPos.value = props.horizontal ? event.clientX : event.clientY
  startSizes.value = [...sizes.value]

  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
  document.body.style.cursor = props.horizontal ? 'col-resize' : 'row-resize'
  document.body.style.userSelect = 'none'
}

const onResize = (event: MouseEvent) => {
  if (!resizing.value) return

  const containers = document.querySelectorAll('.resizable-panes')
  let container: HTMLElement | null = null

  for (const elem of containers) {
    if (elem.contains(event.target as Node)) {
      container = elem as HTMLElement
      break
    }
  }

  if (!container) return

  const containerRect = container.getBoundingClientRect()
  const containerSize = props.horizontal ? containerRect.width : containerRect.height
  const currentPos = props.horizontal ? event.clientX : event.clientY
  const delta = currentPos - startPos.value
  const deltaPercent = (delta / containerSize) * 100

  const newSizes = [...startSizes.value]
  const leftIndex = resizingIndex.value
  const rightIndex = leftIndex + 1

  const newLeftSize = startSizes.value[leftIndex] + deltaPercent
  const newRightSize = startSizes.value[rightIndex] - deltaPercent

  if (newLeftSize >= 10 && newRightSize >= 10) {
    newSizes[leftIndex] = newLeftSize
    newSizes[rightIndex] = newRightSize
    sizes.value = newSizes
  }
}

const stopResize = () => {
  resizing.value = false
  resizingIndex.value = -1
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}
</script>

<style scoped>
.resizable-panes {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.resizable-panes.horizontal {
  display: flex;
  flex-direction: row;
}

.resizable-panes.vertical {
  display: flex;
  flex-direction: column;
}

.pane {
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
}

.divider {
  position: absolute;
  z-index: 100;
  background: transparent;
  transition: background 0.1s ease;
}

.divider:hover {
  background: var(--color-primary);
}

.divider:active {
  background: var(--color-primary-hover);
}

.divider-handle {
  width: 100%;
  height: 100%;
}

.resizable-panes.horizontal .divider {
  width: 4px;
  height: 100%;
  margin-left: -2px;
}

.resizable-panes.vertical .divider {
  width: 100%;
  height: 4px;
  margin-top: -2px;
}
</style>
