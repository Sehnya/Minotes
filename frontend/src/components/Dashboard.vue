<template>
  <div class="dashboard">
    <h1>Welcome, {{ user?.username || "..." }}</h1>

    <input
      v-model="title"
      placeholder="Note title"
      class="note-title"
    />

    <EditorContent :editor="editor" class="editor"/>

    <button @click="saveNote" class="save-button">Save Note</button>

    <h2>Your Notes</h2>
    <ul v-if="notes.length">
      <li v-for="note in notes" :key="note.id">
        <strong>{{ note.title }}</strong>
        <div v-html="note.content" />
      </li>
    </ul>
    <p v-else>No notes yet.</p>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Editor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'

const user = ref(null)
const notes = ref([])
const title = ref('')

// Initialize TipTap editor
const editor = new Editor({
  content: '<p>Start typing...</p>',
  extensions: [StarterKit],
})

// Fetch logged-in user
const fetchUser = async () => {
  try {
    const res = await fetch('http://localhost:5000/api/session', {
      credentials: 'include',
    })

    if (!res.ok) {
      window.location.href = 'http://localhost:5000/login'
      return
    }

    user.value = await res.json()
    await fetchNotes()
  } catch (error) {
    console.error("Error fetching session:", error)
  }
}

// Fetch notes for logged-in user
const fetchNotes = async () => {
  try {
    const res = await fetch('http://localhost:5000/api/notes', {
      credentials: 'include',
    })
    const data = await res.json()
    notes.value = data.notes || []
  } catch (err) {
    console.error("Error fetching notes:", err)
  }
}

// Save new note to backend
const saveNote = async () => {
  try {
    const response = await fetch('http://localhost:5000/save_note', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        title: title.value,
        content: editor.getHTML(),
      }),
    })

    const result = await response.json()
    alert(result.message || 'Note saved.')

    // Reset form
    title.value = ''
    editor.commands.setContent('')
    await fetchNotes()
  } catch (error) {
    console.error("Error saving note:", error)
  }
}

onMounted(fetchUser)
onBeforeUnmount(() => {
  editor.destroy()
})
</script>

<style scoped>
.dashboard {
  max-width: 700px;
  margin: auto;

}
.note-title {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
}
.editor {
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 1rem;
  min-height: 200px;
  margin-bottom: 1rem;
}
.save-button {
  padding: 0.75rem 1.5rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
</style>
