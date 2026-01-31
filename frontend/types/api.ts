export interface Block {
  type: string
  label: string | null
  title: string | null
  id: string
  range: [number, number]
  latex_fragment: string
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
}

// Git型定義

export interface GitFileStatus {
  path: string
  status: string
  staged: boolean
}

export interface GitStatus {
  is_repo: boolean
  branch: string
  staged: GitFileStatus[]
  unstaged: GitFileStatus[]
}

export interface GitDiff {
  path: string
  old_content: string
  new_content: string
}

export interface GitCommitResult {
  hash: string
  message: string
}

// AI型定義

export interface AIContext {
  type: 'block' | 'selection'
  label: string
  content: string
}
