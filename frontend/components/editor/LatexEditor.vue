<template>
  <div class="latex-editor">
    <textarea
      v-model="localSource"
      @input="onInput"
      placeholder="Enter LaTeX here..."
      class="editor-textarea"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { debounce } from '~/utils/debounce'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const localSource = ref(props.modelValue)

const debouncedEmit = debounce((value: string) => {
  emit('update:modelValue', value)
}, 500)

const onInput = () => {
  debouncedEmit(localSource.value)
}

watch(() => props.modelValue, (newValue) => {
  if (newValue !== localSource.value) {
    localSource.value = newValue
  }
})
</script>

<style scoped>
.latex-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.editor-textarea {
  flex: 1;
  width: 100%;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  padding: 16px;
  border: none;
  resize: none;
  outline: none;
  background: #1e1e1e;
  color: #d4d4d4;
  overflow-y: auto;
}
</style>
