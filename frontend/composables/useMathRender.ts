import katex from 'katex'

export function useMathRender() {
  const renderMath = (text: string): string => {
    if (!text) return ''

    // Replace inline math $...$ with rendered HTML
    return text.replace(/\$([^$]+)\$/g, (_, math) => {
      try {
        return katex.renderToString(math, {
          throwOnError: false,
          displayMode: false
        })
      } catch {
        return `$${math}$`
      }
    })
  }

  return { renderMath }
}
