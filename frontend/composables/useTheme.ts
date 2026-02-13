import { ref, onMounted, watch } from 'vue'

type Theme = 'light' | 'dark'

const currentTheme = ref<Theme>('light')

export function useTheme() {
  const setTheme = (theme: Theme) => {
    currentTheme.value = theme
    if (import.meta.client) {
      document.documentElement.setAttribute('data-theme', theme)
      localStorage.setItem('theme', theme)
    }
  }

  const toggleTheme = () => {
    setTheme(currentTheme.value === 'dark' ? 'light' : 'dark')
  }

  const initTheme = () => {
    if (import.meta.client) {
      const savedTheme = localStorage.getItem('theme') as Theme | null
      if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
        setTheme(savedTheme)
      } else {
        setTheme('light')
      }
    }
  }

  onMounted(() => {
    initTheme()
  })

  return {
    theme: currentTheme,
    setTheme,
    toggleTheme,
    initTheme
  }
}
