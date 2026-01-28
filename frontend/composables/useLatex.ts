import { computed } from 'vue'
import type { Note, Block } from '~/types/api'

export function useLatex(note: Ref<Note | null>) {
  const blocks = computed(() => note.value?.blocks || [])
  const todos = computed(() => note.value?.todos || [])

  const getBlockById = (blockId: string): Block | undefined => {
    return blocks.value.find((b) => b.id === blockId)
  }

  const definitions = computed(() => blocks.value.filter((b) => b.type === 'definition'))

  return {
    blocks,
    todos,
    definitions,
    getBlockById
  }
}
