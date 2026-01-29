import type {
  ParseResult,
  SkeletonCard,
  LeanGeneration,
  LeanCheckResult,
  FileNode,
  FileContent
} from '~/types/api'

const API_BASE = '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  })
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }
  return response.json()
}

export function parseLatex(latexSource: string): Promise<ParseResult> {
  return request('/parse', {
    method: 'POST',
    body: JSON.stringify({ latex_source: latexSource })
  })
}

export function generateSkeleton(
  filePath: string,
  blockId: string
): Promise<{ cards: SkeletonCard[] }> {
  return request('/assist/skeleton', {
    method: 'POST',
    body: JSON.stringify({ file_path: filePath, block_id: blockId })
  })
}

export function generateLean(filePath: string, blockId: string): Promise<LeanGeneration> {
  return request('/assist/lean/generate', {
    method: 'POST',
    body: JSON.stringify({ file_path: filePath, block_id: blockId })
  })
}

export function checkLean(leanCode: string, imports: string[]): Promise<LeanCheckResult> {
  return request('/lean/check', {
    method: 'POST',
    body: JSON.stringify({ lean_code: leanCode, imports })
  })
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

// Workspace API

export function getWorkspace(): Promise<{ path: string }> {
  return request('/files/workspace')
}

export function browseDirectory(path?: string): Promise<{ current: string; dirs: string[] }> {
  const params = path ? `?path=${encodeURIComponent(path)}` : ''
  return request(`/files/workspace/browse${params}`)
}

export function changeWorkspace(path: string): Promise<FileNode[]> {
  return request('/files/workspace', {
    method: 'PUT',
    body: JSON.stringify({ path })
  })
}

// File API

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
