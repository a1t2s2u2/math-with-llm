export interface Note {
  note_id: string
  title: string
  latex_source: string
  rendered_html: string
  blocks: Block[]
  symbols: Symbol[]
  todos: Todo[]
  lean_artifacts: Record<string, LeanArtifact>
}

export interface Block {
  type: string
  label: string | null
  id: string
  range: [number, number]
  latex_fragment: string
}

export interface Symbol {
  name: string
  first_occurrence_pos: number
}

export interface Todo {
  content: string
  line_number: number
}

export interface LeanArtifact {
  block_id: string
  lean_code: string | null
  diagnostics: any[]
  logs: string | null
  patches: string[]
}

export interface ParseResult {
  blocks: Block[]
  symbols: Symbol[]
  todos: Todo[]
  renderer_errors: string[]
}

export interface SkeletonCard {
  strategy: string
  description: string
  required_lemmas: string[]
  assumptions_to_check: string[]
}

export interface LeanGeneration {
  lean_code: string
  imports: string[]
  notes: string
}

export interface LeanCheckResult {
  status: string
  diagnostics: Diagnostic[]
  logs: string
  duration_ms: number
}

export interface Diagnostic {
  line: number
  column: number
  severity: string
  message: string
}

export interface FileNode {
  name: string
  type: 'file' | 'directory'
  path: string
  children?: FileNode[]
}

export interface FileContent {
  path: string
  name: string
  content: string
  rendered_html: string
  blocks: Block[]
  symbols: Symbol[]
  todos: Todo[]
}
