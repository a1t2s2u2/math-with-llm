<template>
  <div class="home-page">
    <div class="container">
      <h1>Math with LLM</h1>
      <p>LaTeX editor with LLM assistance and Lean verification</p>

      <div class="actions">
        <button class="create-button" @click="createNewNote">Create New Note</button>
      </div>

      <div v-if="notes.length > 0" class="notes-list">
        <h2>Recent Notes</h2>
        <div v-for="note in notes" :key="note.note_id" class="note-item">
          <NuxtLink :to="`/notes/${note.note_id}`">
            {{ note.title }}
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { createNote } from '~/utils/api'
import type { Note } from '~/types/api'

const notes = ref<Note[]>([])

const createNewNote = async () => {
  const title = prompt('Enter note title:')
  if (!title) return

  try {
    const note = await createNote(title)
    await navigateTo(`/notes/${note.note_id}`)
  } catch (error) {
    console.error('Failed to create note:', error)
    alert('Failed to create note')
  }
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  padding: 40px 20px;
  background: #f5f5f5;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  font-size: 36px;
  margin-bottom: 8px;
}

p {
  color: #666;
  margin-bottom: 32px;
}

.create-button {
  padding: 12px 24px;
  background: #007acc;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
}

.create-button:hover {
  background: #005a9e;
}

.notes-list {
  margin-top: 40px;
}

.notes-list h2 {
  font-size: 24px;
  margin-bottom: 16px;
}

.note-item {
  padding: 16px;
  background: white;
  margin-bottom: 8px;
  border-radius: 6px;
  border: 1px solid #ddd;
}

.note-item a {
  text-decoration: none;
  color: #007acc;
  font-weight: 500;
}

.note-item a:hover {
  text-decoration: underline;
}
</style>
