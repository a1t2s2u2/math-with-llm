import { ref } from 'vue'
import { getNote, updateNote as apiUpdateNote } from '~/utils/api'
import type { Note } from '~/types/api'
import { debounce } from '~/utils/debounce'

export function useNote(noteId: string) {
  const note = ref<Note | null>(null)
  const loading = ref(false)

  const load = async () => {
    loading.value = true
    note.value = await getNote(noteId)
    loading.value = false
  }

  const debouncedUpdate = debounce(async (source: string) => {
    if (!note.value) return
    note.value = await apiUpdateNote(noteId, source)
  }, 1000)

  const updateSource = (source: string) => {
    if (note.value) {
      note.value.latex_source = source
    }
    debouncedUpdate(source)
  }

  return {
    note,
    loading,
    load,
    updateSource
  }
}
