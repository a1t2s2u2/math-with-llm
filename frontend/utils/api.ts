import type {
  Note,
  ParseResult,
  SkeletonCard,
  LeanGeneration,
  LeanCheckResult,
  FileNode,
  FileContent
} from '~/types/api'

const API_BASE = '/api'

export async function createNote(title: string): Promise<Note> {
  const response = await fetch(`${API_BASE}/notes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  })
  if (!response.ok) throw new Error('Failed to create note')
  return response.json()
}

export async function getNote(noteId: string): Promise<Note> {
  const response = await fetch(`${API_BASE}/notes/${noteId}`)
  if (!response.ok) throw new Error('Failed to get note')
  return response.json()
}

export async function updateNote(noteId: string, latexSource: string): Promise<Note> {
  const response = await fetch(`${API_BASE}/notes/${noteId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ latex_source: latexSource })
  })
  if (!response.ok) throw new Error('Failed to update note')
  return response.json()
}

export async function parseLatex(latexSource: string): Promise<ParseResult> {
  const response = await fetch(`${API_BASE}/parse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ latex_source: latexSource })
  })
  if (!response.ok) throw new Error('Failed to parse')
  return response.json()
}

export async function generateSkeleton(
  noteId: string,
  blockId: string
): Promise<{ cards: SkeletonCard[] }> {
  const response = await fetch(`${API_BASE}/assist/skeleton`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ note_id: noteId, block_id: blockId })
  })
  if (!response.ok) throw new Error('Failed to generate skeleton')
  return response.json()
}

export async function generateLean(noteId: string, blockId: string): Promise<LeanGeneration> {
  const response = await fetch(`${API_BASE}/assist/lean/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ note_id: noteId, block_id: blockId })
  })
  if (!response.ok) throw new Error('Failed to generate Lean')
  return response.json()
}

export async function checkLean(leanCode: string, imports: string[]): Promise<LeanCheckResult> {
  const response = await fetch(`${API_BASE}/lean/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lean_code: leanCode, imports })
  })
  if (!response.ok) throw new Error('Failed to check Lean')
  return response.json()
}

export async function generateFileSkeletonApi(
  filePath: string,
  blockId: string
): Promise<{ cards: SkeletonCard[] }> {
  const response = await fetch(`${API_BASE}/assist/file/skeleton`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_path: filePath, block_id: blockId })
  })
  if (!response.ok) throw new Error('Failed to generate skeleton')
  return response.json()
}

export async function generateFileLeanApi(
  filePath: string,
  blockId: string
): Promise<LeanGeneration> {
  const response = await fetch(`${API_BASE}/assist/file/lean/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_path: filePath, block_id: blockId })
  })
  if (!response.ok) throw new Error('Failed to generate Lean')
  return response.json()
}

export async function chatApi(
  message: string,
  contextType: string | null,
  contextContent: string | null
): Promise<{ response: string }> {
  const response = await fetch(`${API_BASE}/assist/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      context_type: contextType,
      context_content: contextContent
    })
  })
  if (!response.ok) throw new Error('Failed to chat')
  return response.json()
}

// File API

export async function getFileTree(): Promise<FileNode[]> {
  const response = await fetch(`${API_BASE}/files/tree`)
  if (!response.ok) throw new Error('Failed to get file tree')
  return response.json()
}

export async function getFile(path: string): Promise<FileContent> {
  const response = await fetch(`${API_BASE}/files/${encodeURIComponent(path)}`)
  if (!response.ok) throw new Error('Failed to get file')
  return response.json()
}

export async function updateFile(path: string, content: string): Promise<FileContent> {
  const response = await fetch(`${API_BASE}/files/${encodeURIComponent(path)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content })
  })
  if (!response.ok) throw new Error('Failed to update file')
  return response.json()
}

export async function createFile(path: string, content: string = ''): Promise<FileContent> {
  const response = await fetch(`${API_BASE}/files`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path, content })
  })
  if (!response.ok) throw new Error('Failed to create file')
  return response.json()
}

export async function deleteFile(path: string): Promise<void> {
  const response = await fetch(`${API_BASE}/files/${encodeURIComponent(path)}`, {
    method: 'DELETE'
  })
  if (!response.ok) throw new Error('Failed to delete file')
}

export async function renameFile(oldPath: string, newPath: string): Promise<FileContent> {
  const response = await fetch(`${API_BASE}/files/rename`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ old_path: oldPath, new_path: newPath })
  })
  if (!response.ok) throw new Error('Failed to rename file')
  return response.json()
}

export async function createFolder(path: string): Promise<FileNode> {
  const response = await fetch(`${API_BASE}/files/folders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path })
  })
  if (!response.ok) throw new Error('Failed to create folder')
  return response.json()
}

export async function deleteFolder(path: string): Promise<void> {
  const response = await fetch(`${API_BASE}/files/folders/${encodeURIComponent(path)}`, {
    method: 'DELETE'
  })
  if (!response.ok) throw new Error('Failed to delete folder')
}
