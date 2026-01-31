export const BLOCK_TYPE_LABELS: Record<string, string> = {
  definition: '定義',
  theorem: '定理',
  lemma: '補題',
  proposition: '命題',
  corollary: '系',
  proof: '証明',
  remark: '注意',
  example: '例'
}

export const BLOCK_TYPE_SHORT: Record<string, string> = {
  definition: 'Def',
  theorem: 'Thm',
  lemma: 'Lem',
  proposition: 'Prop',
  corollary: 'Cor',
  proof: 'Proof',
  remark: 'Rem',
  example: 'Ex'
}

export const PROVABLE_BLOCK_TYPES = new Set([
  'definition',
  'lemma',
  'theorem',
  'proposition',
  'corollary'
])
