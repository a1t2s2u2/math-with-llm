import { ref } from 'vue'
import { getFile, updateFile as apiUpdateFile } from '~/utils/api'
import type { FileContent } from '~/types/api'
import { debounce } from '~/utils/debounce'

export function useFile() {
  const file = ref<FileContent | null>(null)
  const loading = ref(false)
  const currentPath = ref<string | null>(null)

  const load = async (path: string) => {
    loading.value = true
    currentPath.value = path
    file.value = await getFile(path)
    loading.value = false
  }

  const debouncedUpdate = debounce(async (path: string, content: string) => {
    file.value = await apiUpdateFile(path, content)
  }, 1000)

  const updateContent = (content: string) => {
    if (file.value && currentPath.value) {
      file.value.content = content
      debouncedUpdate(currentPath.value, content)
    }
  }

  const clear = () => {
    file.value = null
    currentPath.value = null
  }

  return {
    file,
    loading,
    currentPath,
    load,
    updateContent,
    clear
  }
}
