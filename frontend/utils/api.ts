import type {
  FileNode,
  FileContent,
  ChatMessage,
  GitStatus,
  GitDiff,
  GitCommitResult,
  SkeletonCard,
  BlockReference
} from '~/types/api'

const API_BASE = '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  })
  if (!response.ok) {
    const body = await response.text()
    throw new Error(`API error ${response.status}: ${body}`)
  }
  return response.json()
}

export function chatApi(
  message: string,
  contextType: string | null,
  contextContent: string | null
): Promise<{ response: string }> {
  return request('/assist/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      context_type: contextType,
      context_content: contextContent
    })
  })
}

export async function chatStreamApi(
  message: string,
  contextType: string | null,
  contextContent: string | null,
  onChunk: (text: string) => void,
  options?: {
    filePath?: string
    blockId?: string
    history?: ChatMessage[]
    onReferences?: (refs: BlockReference[]) => void
  }
): Promise<void> {
  const body: Record<string, unknown> = {
    message,
    context_type: contextType,
    context_content: contextContent
  }
  if (options?.filePath) body.file_path = options.filePath
  if (options?.blockId) body.block_id = options.blockId
  if (options?.history?.length) body.history = options.history

  const response = await fetch(`${API_BASE}/assist/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(`API error ${response.status}: ${text}`)
  }

  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop()!

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      const data = line.slice(6)
      if (data === '[DONE]') return
      const parsed = JSON.parse(data)
      if (parsed.references && options?.onReferences) {
        options.onReferences(parsed.references)
      } else if (parsed.content) {
        onChunk(parsed.content)
      }
    }
  }
}

// ワークスペースAPI

export function getWorkspace(): Promise<{ path: string }> {
  return request('/files/workspace')
}

export function pickWorkspace(): Promise<{ tree: FileNode[] | null; path?: string }> {
  return request('/files/workspace/pick', { method: 'POST' })
}

export function changeWorkspace(path: string): Promise<FileNode[]> {
  return request('/files/workspace', {
    method: 'PUT',
    body: JSON.stringify({ path })
  })
}

// ファイルAPI

export function getFileTree(): Promise<FileNode[]> {
  return request('/files/tree')
}

export function getFile(path: string): Promise<FileContent> {
  return request(`/files/${encodeURIComponent(path)}`)
}

export function updateFile(path: string, content: string): Promise<FileContent> {
  return request(`/files/${encodeURIComponent(path)}`, {
    method: 'PUT',
    body: JSON.stringify({ content })
  })
}

export function createFile(path: string, content: string = ''): Promise<FileContent> {
  return request('/files', {
    method: 'POST',
    body: JSON.stringify({ path, content })
  })
}

export async function deleteFile(path: string): Promise<void> {
  await request(`/files/${encodeURIComponent(path)}`, {
    method: 'DELETE'
  })
}

export function renameFile(oldPath: string, newPath: string): Promise<FileContent> {
  return request('/files/rename', {
    method: 'POST',
    body: JSON.stringify({ old_path: oldPath, new_path: newPath })
  })
}

export function createFolder(path: string): Promise<FileNode> {
  return request('/files/folders', {
    method: 'POST',
    body: JSON.stringify({ path })
  })
}

export async function deleteFolder(path: string): Promise<void> {
  await request(`/files/folders/${encodeURIComponent(path)}`, {
    method: 'DELETE'
  })
}

// Git API

export function getGitStatus(): Promise<GitStatus> {
  return request('/git/status')
}

export function getGitOriginal(path: string): Promise<{ content: string }> {
  return request(`/git/original?path=${encodeURIComponent(path)}`)
}

export function getGitDiff(path: string, staged: boolean = false): Promise<GitDiff> {
  return request(`/git/diff?path=${encodeURIComponent(path)}&staged=${staged}`)
}

export function initGitRepo(): Promise<{ status: string }> {
  return request('/git/init', { method: 'POST' })
}

export function stageFiles(paths: string[]): Promise<{ status: string }> {
  return request('/git/stage', {
    method: 'POST',
    body: JSON.stringify({ paths })
  })
}

export function unstageFiles(paths: string[]): Promise<{ status: string }> {
  return request('/git/unstage', {
    method: 'POST',
    body: JSON.stringify({ paths })
  })
}

export function discardFiles(paths: string[]): Promise<{ status: string }> {
  return request('/git/discard', {
    method: 'POST',
    body: JSON.stringify({ paths })
  })
}

export function gitCommit(message: string): Promise<GitCommitResult> {
  return request('/git/commit', {
    method: 'POST',
    body: JSON.stringify({ message })
  })
}

// Skeleton API

export function generateSkeleton(
  filePath: string,
  blockId: string
): Promise<{ cards: SkeletonCard[] }> {
  return request('/assist/skeleton', {
    method: 'POST',
    body: JSON.stringify({ file_path: filePath, block_id: blockId })
  })
}

// Handwriting API

export async function convertHandwriting(imageBlob: Blob): Promise<{ latex: string }> {
  const formData = new FormData()
  formData.append('file', imageBlob, 'handwriting.png')

  const response = await fetch(`${API_BASE}/handwriting/convert`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    const body = await response.text()
    throw new Error(`API error ${response.status}: ${body}`)
  }

  return response.json()
}
