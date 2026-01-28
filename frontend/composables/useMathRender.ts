import katex from 'katex'

export function useMathRender() {
  const renderMath = (text: string): string => {
    if (!text) return ''

    let result = text

    // Replace display math \[...\]
    result = result.replace(/\\\[([\s\S]+?)\\\]/g, (_, math) => {
      try {
        return katex.renderToString(math.trim(), {
          throwOnError: false,
          displayMode: true
        })
      } catch {
        return `\\[${math}\\]`
      }
    })

    // Replace display math $$...$$
    result = result.replace(/\$\$([\s\S]+?)\$\$/g, (_, math) => {
      try {
        return katex.renderToString(math.trim(), {
          throwOnError: false,
          displayMode: true
        })
      } catch {
        return `$$${math}$$`
      }
    })

    // Replace inline math \(...\)
    result = result.replace(/\\\(([\s\S]+?)\\\)/g, (_, math) => {
      try {
        return katex.renderToString(math.trim(), {
          throwOnError: false,
          displayMode: false
        })
      } catch {
        return `\\(${math}\\)`
      }
    })

    // Replace inline math $...$ (but not $$)
    result = result.replace(/\$([^$\n]+?)\$/g, (_, math) => {
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
