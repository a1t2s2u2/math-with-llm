import katex from 'katex'

export function useMathRender() {
  const renderMath = (text: string): string => {
    if (!text) return ''

    // Replace display math $$...$$ first
    let result = text.replace(/\$\$([^$]+)\$\$/g, (_, math) => {
      try {
        return katex.renderToString(math.trim(), {
          throwOnError: false,
          displayMode: true
        })
      } catch {
        return `$$${math}$$`
      }
    })

    // Replace inline math $...$
    result = result.replace(/\$([^$]+)\$/g, (_, math) => {
      try {
        return katex.renderToString(math, {
          throwOnError: false,
          displayMode: false
        })
      } catch {
        return `$${math}$`
      }
    })

    return result
  }

  return { renderMath }
}
