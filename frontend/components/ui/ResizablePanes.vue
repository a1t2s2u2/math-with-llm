<template>
  <div
    ref="containerRef"
    class="resizable-panes"
    :class="{ horizontal, vertical: !horizontal, dragging: resizing }"
  >
    <div
      v-for="(pane, index) in panes"
      :key="index"
      class="pane"
      :class="{ collapsed: collapsed.has(index) }"
      :style="getPaneStyle(index)"
    >
      <slot :name="`pane-${index}`" />
    </div>
    <div
      v-for="(_, index) in panes.slice(0, -1)"
      :key="`divider-${index}`"
      class="divider"
      :class="{ 'divider-collapsed': hasBorderCollapsed(index) }"
      :style="getDividerStyle(index)"
      @mousedown="startResize(index, $event)"
      @dblclick="toggleCollapse(index)"
    >
      <div class="divider-handle" />
      <div
        v-if="hasBorderCollapsed(index)"
        class="collapse-indicator"
        :class="collapseIndicatorDirection(index)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const COLLAPSE_THRESHOLD = 3
const MIN_SIZE = 10

const props = defineProps<{
  horizontal?: boolean
  initialSizes?: number[]
  collapsible?: boolean
  collapsiblePanes?: number[]
}>()

const panes = computed(() => {
  const count = props.initialSizes?.length || 2
  return Array(count).fill(0)
})

const containerRef = ref<HTMLElement | null>(null)
const sizes = ref<number[]>(props.initialSizes || [50, 50])
const collapsed = ref<Set<number>>(new Set())
const preCollapseSize = ref<Map<number, number>>(new Map())

const resizing = ref(false)
const resizingIndex = ref(-1)
const pairTotal = ref(0)
const pairOffset = ref(0)

const isCollapsible = (index: number) => {
  return props.collapsible && (props.collapsiblePanes?.includes(index) ?? false)
}

const hasBorderCollapsed = (index: number) => {
  return collapsed.value.has(index) || collapsed.value.has(index + 1)
}

const collapseIndicatorDirection = (index: number) => {
  if (collapsed.value.has(index)) return 'indicator-right'
  if (collapsed.value.has(index + 1)) return 'indicator-left'
  return ''
}

const getPaneStyle = (index: number) => {
  if (collapsed.value.has(index)) {
    return props.horizontal
      ? { width: '0%', height: '100%', overflow: 'hidden' }
      : { width: '100%', height: '0%', overflow: 'hidden' }
  }
  const size = sizes.value[index]
  if (props.horizontal) {
    return { width: `${size}%`, height: '100%' }
  }
  return { width: '100%', height: `${size}%` }
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

const toggleCollapse = (dividerIndex: number) => {
  const left = dividerIndex
  const right = dividerIndex + 1

  const target =
    collapsed.value.has(left) && isCollapsible(left)
      ? left
      : collapsed.value.has(right) && isCollapsible(right)
        ? right
        : -1

  if (target === -1) return

  const restoreSize = preCollapseSize.value.get(target) || (props.initialSizes?.[target] ?? 20)
  const neighbor = target === 0 ? 1 : target - 1
  const newSizes = [...sizes.value]

  newSizes[target] = restoreSize
  newSizes[neighbor] -= restoreSize
  if (newSizes[neighbor] < MIN_SIZE) newSizes[neighbor] = MIN_SIZE

  collapsed.value.delete(target)
  preCollapseSize.value.delete(target)
  sizes.value = newSizes
}

const startResize = (index: number, event: MouseEvent) => {
  event.preventDefault()
  resizing.value = true
  resizingIndex.value = index

  const left = index
  const right = index + 1
  pairTotal.value = sizes.value[left] + sizes.value[right]
  pairOffset.value = sizes.value.slice(0, left).reduce((a, b) => a + b, 0)

  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
  document.body.style.cursor = props.horizontal ? 'col-resize' : 'row-resize'
  document.body.style.userSelect = 'none'
}

const onResize = (event: MouseEvent) => {
  if (!resizing.value || !containerRef.value) return

  const rect = containerRef.value.getBoundingClientRect()
  const containerSize = props.horizontal ? rect.width : rect.height
  const containerStart = props.horizontal ? rect.left : rect.top
  const mousePos = props.horizontal ? event.clientX : event.clientY
  const mousePercent = ((mousePos - containerStart) / containerSize) * 100

  const left = resizingIndex.value
  const right = left + 1
  const total = pairTotal.value
  const desiredLeft = mousePercent - pairOffset.value

  let finalLeft: number
  let finalRight: number

  // --- Left pane ---
  if (isCollapsible(left)) {
    if (collapsed.value.has(left)) {
      if (desiredLeft > COLLAPSE_THRESHOLD) {
        collapsed.value.delete(left)
        finalLeft = Math.max(desiredLeft, MIN_SIZE)
      } else {
        finalLeft = 0
      }
    } else if (desiredLeft <= COLLAPSE_THRESHOLD) {
      preCollapseSize.value.set(left, sizes.value[left])
      collapsed.value.add(left)
      finalLeft = 0
    } else {
      finalLeft = Math.max(desiredLeft, MIN_SIZE)
    }
  } else {
    finalLeft = Math.max(desiredLeft, MIN_SIZE)
  }

  finalRight = total - finalLeft

  // --- Right pane ---
  if (isCollapsible(right)) {
    if (collapsed.value.has(right)) {
      if (finalRight > COLLAPSE_THRESHOLD) {
        collapsed.value.delete(right)
        finalRight = Math.max(finalRight, MIN_SIZE)
        finalLeft = total - finalRight
      } else {
        finalRight = 0
        finalLeft = total
      }
    } else if (finalRight <= COLLAPSE_THRESHOLD) {
      preCollapseSize.value.set(right, sizes.value[right])
      collapsed.value.add(right)
      finalRight = 0
      finalLeft = total
    } else if (finalRight < MIN_SIZE) {
      finalRight = MIN_SIZE
      finalLeft = total - MIN_SIZE
    }
  } else if (finalRight < MIN_SIZE) {
    finalRight = MIN_SIZE
    finalLeft = total - MIN_SIZE
  }

  const newSizes = [...sizes.value]
  newSizes[left] = finalLeft
  newSizes[right] = finalRight
  sizes.value = newSizes
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
  transition:
    width 0.15s ease,
    height 0.15s ease;
}

.dragging .pane {
  transition: none;
}

.pane.collapsed {
  overflow: hidden;
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

.divider-collapsed {
  background: var(--color-border);
}

.divider-collapsed:hover {
  background: var(--color-primary);
}

.divider-handle {
  width: 100%;
  height: 100%;
}

.collapse-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 0;
  height: 0;
  border: 4px solid transparent;
}

.collapse-indicator.indicator-right {
  border-left: 5px solid var(--color-text-muted);
  border-right: none;
}

.collapse-indicator.indicator-left {
  border-right: 5px solid var(--color-text-muted);
  border-left: none;
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
