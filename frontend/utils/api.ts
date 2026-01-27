import type { Note, ParseResult, SkeletonCard, LeanGeneration, LeanCheckResult } from '~/types/api'

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

export async function generateSkeleton(noteId: string, blockId: string): Promise<{ cards: SkeletonCard[] }> {
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
