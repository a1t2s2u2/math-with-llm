import { ref } from 'vue'
import { checkLean } from '~/utils/api'
import type { LeanCheckResult } from '~/types/api'

export function useLean() {
  const code = ref('')
  const imports = ref<string[]>([])
  const result = ref<LeanCheckResult | null>(null)
  const checking = ref(false)

  const setCode = (newCode: string, newImports: string[] = []) => {
    code.value = newCode
    imports.value = newImports
  }

  const check = async () => {
    checking.value = true
    result.value = await checkLean(code.value, imports.value)
    checking.value = false
  }

  return {
    code,
    imports,
    result,
    checking,
    setCode,
    check
  }
}
