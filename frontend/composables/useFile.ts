import { ref, computed } from 'vue'
import { getFile, updateFile as apiUpdateFile } from '~/utils/api'
import type { FileContent } from '~/types/api'

export function useFile() {
  const file = ref<FileContent | null>(null)
  const loading = ref(false)
  const currentPath = ref<string | null>(null)
  const localContent = ref<string>('')
  const isDirty = computed(() => {
    if (!file.value) return false
    return localContent.value !== file.value.content
  })

  const load = async (path: string) => {
    loading.value = true
    currentPath.value = path
    file.value = await getFile(path)
    localContent.value = file.value?.content || ''
    loading.value = false
  }

  const setLocalContent = (content: string) => {
    localContent.value = content
  }

  const save = async () => {
    if (!currentPath.value || !isDirty.value) return
    file.value = await apiUpdateFile(currentPath.value, localContent.value)
  }

  const clear = () => {
    file.value = null
    currentPath.value = null
    localContent.value = ''
  }

  return {
    file,
    loading,
    currentPath,
    localContent,
    isDirty,
    load,
    setLocalContent,
    save,
    clear
  }
}
