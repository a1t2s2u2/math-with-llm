import { computed } from 'vue'
import type { Note, Block, Symbol, Todo } from '~/types/api'

export function useLatex(note: Ref<Note | null>) {
  const blocks = computed(() => note.value?.blocks || [])
  const symbols = computed(() => note.value?.symbols || [])
  const todos = computed(() => note.value?.todos || [])

  const getBlockById = (blockId: string): Block | undefined => {
    return blocks.value.find(b => b.id === blockId)
  }

  const definitions = computed(() =>
    blocks.value.filter(b => b.type === 'definition')
  )

  return {
    blocks,
    symbols,
    todos,
    definitions,
    getBlockById
  }
}
