<template>
  <div class="resizable-panes" :class="{ horizontal, vertical: !horizontal }">
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

const sizes = ref<number[]>(props.initialSizes || [50, 50])
const collapsed = ref<Set<number>>(new Set())
const preCollapseSize = ref<Map<number, number>>(new Map())

const resizing = ref(false)
const resizingIndex = ref(-1)
const startPos = ref(0)
const startSizes = ref<number[]>([])

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
  const size = sizes.value[index]
  if (collapsed.value.has(index)) {
    return props.horizontal
      ? { width: '0%', height: '100%', overflow: 'hidden' }
      : { width: '100%', height: '0%', overflow: 'hidden' }
  }
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

const collapsePane = (index: number, newSizes: number[]) => {
  const adjacentIndex = index === 0 ? 1 : index - 1
  preCollapseSize.value.set(index, newSizes[index])
  newSizes[adjacentIndex] += newSizes[index]
  newSizes[index] = 0
  collapsed.value.add(index)
}

const expandPane = (index: number, newSizes: number[]) => {
  const restoreSize = preCollapseSize.value.get(index) || (props.initialSizes?.[index] ?? 20)
  const adjacentIndex = index === 0 ? 1 : index - 1
  newSizes[adjacentIndex] -= restoreSize
  if (newSizes[adjacentIndex] < 10) {
    newSizes[adjacentIndex] = 10
  }
  newSizes[index] = restoreSize
  collapsed.value.delete(index)
  preCollapseSize.value.delete(index)
}

const toggleCollapse = (dividerIndex: number) => {
  const leftIndex = dividerIndex
  const rightIndex = dividerIndex + 1

  // Check if a neighboring pane is collapsed and restore it
  if (collapsed.value.has(leftIndex) && isCollapsible(leftIndex)) {
    const newSizes = [...sizes.value]
    expandPane(leftIndex, newSizes)
    sizes.value = newSizes
    return
  }
  if (collapsed.value.has(rightIndex) && isCollapsible(rightIndex)) {
    const newSizes = [...sizes.value]
    expandPane(rightIndex, newSizes)
    sizes.value = newSizes
    return
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

  // If a collapsed pane is being dragged open
  if (collapsed.value.has(leftIndex) && isCollapsible(leftIndex) && deltaPercent < -5) {
    expandPane(leftIndex, newSizes)
    sizes.value = newSizes
    // Reset start state for continued drag
    startSizes.value = [...sizes.value]
    startPos.value = currentPos
    return
  }
  if (collapsed.value.has(rightIndex) && isCollapsible(rightIndex) && deltaPercent > 5) {
    expandPane(rightIndex, newSizes)
    sizes.value = newSizes
    startSizes.value = [...sizes.value]
    startPos.value = currentPos
    return
  }

  let newLeftSize = startSizes.value[leftIndex] + deltaPercent
  let newRightSize = startSizes.value[rightIndex] - deltaPercent

  // Collapsible panes: snap to 0 at threshold
  if (isCollapsible(leftIndex) && newLeftSize <= 5 && newLeftSize < startSizes.value[leftIndex]) {
    collapsePane(leftIndex, newSizes)
    sizes.value = newSizes
    startSizes.value = [...sizes.value]
    startPos.value = currentPos
    return
  }
  if (
    isCollapsible(rightIndex) &&
    newRightSize <= 5 &&
    newRightSize < startSizes.value[rightIndex]
  ) {
    collapsePane(rightIndex, newSizes)
    sizes.value = newSizes
    startSizes.value = [...sizes.value]
    startPos.value = currentPos
    return
  }

  // Normal resize with minimum constraint
  const leftMin = collapsed.value.has(leftIndex) ? 0 : 10
  const rightMin = collapsed.value.has(rightIndex) ? 0 : 10

  if (newLeftSize >= leftMin && newRightSize >= rightMin) {
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
  transition:
    width 0.15s ease,
    height 0.15s ease;
}

.pane.collapsed {
  width: 0 !important;
  height: 0 !important;
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
