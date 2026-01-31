/** LCS のインデックスペア [oldIdx, newIdx][] を返す */
export function buildLCSIndices(a: string[], b: string[]): [number, number][] {
  const m = a.length
  const n = b.length
  if (m * n > 5_000_000) return []

  const dp: number[][] = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0))
  for (let i = m - 1; i >= 0; i--) {
    for (let j = n - 1; j >= 0; j--) {
      if (a[i] === b[j]) {
        dp[i][j] = dp[i + 1][j + 1] + 1
      } else {
        dp[i][j] = Math.max(dp[i + 1][j], dp[i][j + 1])
      }
    }
  }

  const result: [number, number][] = []
  let i = 0
  let j = 0
  while (i < m && j < n) {
    if (a[i] === b[j]) {
      result.push([i, j])
      i++
      j++
    } else if (dp[i + 1][j] >= dp[i][j + 1]) {
      i++
    } else {
      j++
    }
  }
  return result
}

/** 類似度ベースで old 行と new 行をマッチングし、modified と判定された new 行のインデックスを返す */
export function matchBySimilarity(oldGap: string[], newGap: string[]): Set<number> {
  const pairs: { oi: number; ni: number; sim: number }[] = []
  for (let i = 0; i < oldGap.length; i++) {
    for (let j = 0; j < newGap.length; j++) {
      pairs.push({ oi: i, ni: j, sim: lineSimilarity(oldGap[i], newGap[j]) })
    }
  }
  // 類似度の高い順にグリーディマッチ
  pairs.sort((a, b) => b.sim - a.sim)
  const usedOld = new Set<number>()
  const usedNew = new Set<number>()
  for (const { oi, ni, sim } of pairs) {
    if (sim < 0.3) break
    if (usedOld.has(oi) || usedNew.has(ni)) continue
    usedOld.add(oi)
    usedNew.add(ni)
  }
  return usedNew
}

/** 2 行の位置ベース文字一致率 */
export function lineSimilarity(a: string, b: string): number {
  const maxLen = Math.max(a.length, b.length)
  if (maxLen === 0) return 1
  let matches = 0
  const minLen = Math.min(a.length, b.length)
  for (let i = 0; i < minLen; i++) {
    if (a[i] === b[i]) matches++
  }
  return matches / maxLen
}
