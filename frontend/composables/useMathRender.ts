import katex from 'katex'

export function useMathRender() {
  const renderMath = (text: string): string => {
    if (!text) return ''

    const placeholders: Map<string, string> = new Map()
    let counter = 0
    let result = text

    const replaceWith = (math: string, displayMode: boolean): string => {
      const id = `\x00MATH_${counter++}\x00`
      try {
        placeholders.set(
          id,
          katex.renderToString(math.trim(), {
            throwOnError: false,
            displayMode
          })
        )
      } catch {
        placeholders.set(id, displayMode ? `$$${math}$$` : `$${math}$`)
      }
      return id
    }

    // ディスプレイ数式を先に変換（長いデリミタ優先）
    result = result.replace(/\\\[([\s\S]+?)\\\]/g, (_, m) => replaceWith(m, true))
    result = result.replace(/\$\$([\s\S]+?)\$\$/g, (_, m) => replaceWith(m, true))

    // インライン数式
    result = result.replace(/\\\(([\s\S]+?)\\\)/g, (_, m) => replaceWith(m, false))
    result = result.replace(/\$([^$]+?)\$/g, (_, m) => replaceWith(m, false))

    // プレースホルダを復元
    for (const [id, html] of placeholders) {
      result = result.replace(id, html)
    }

    return result
  }

  return { renderMath }
}
