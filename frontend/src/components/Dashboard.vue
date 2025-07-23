<template>
  <div class="dashboard">
    <h1>Welcome, {{ user?.username || "..." }}</h1>

    <input v-model="title" placeholder="Note title" class="note-title" />

    <EditorContent :editor="editor" class="editor" />

    <button @click="saveNote" class="save-button">Save Note</button>

    <h2>Your Notes</h2>
    <ul v-if="notes.length">
      <li v-for="note in notes" :key="note.id">
        <strong>{{ note.title }}</strong>
        <div v-html="note.content"></div>
      </li>
    </ul>
    <p v-else>No notes yet.</p>
  </div>
</template>

<script setup>
import {onBeforeUnmount, onMounted, ref} from 'vue'
import {Editor, EditorContent} from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'

const user = ref(null)
const notes = ref([])
const title = ref('')
const editor = new Editor({
  content: '<p>Start typing...</p>',
  extensions: [StarterKit],
})

const fetchUser = async () => {
  const res = await fetch('http://localhost:5000/api/session', {
    credentials: 'include',
  })

  if (!res.ok) {
    window.location.href = 'http://localhost:5000/login'
    return
  }

  user.value = await res.json()
  await fetchNotes()
}

const fetchNotes = async () => {
  const res = await fetch(`http://localhost:5000/api/notes`, {
    credentials: 'include',
  })
  const data = await res.json()
  notes.value = data.notes || []
}

const saveNote = async () => {
  const res = await fetch('http://localhost:5000/save_note', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      title: title.value,
      content: editor.getHTML(),
    }),
  })

  const result = await res.json()
  alert(result.message || 'Note saved.')
  title.value = ''
  editor.commands.setContent('')
  await fetchNotes()
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
  padding: 2rem;
}
.note-title {
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 1rem;
  font-size: 1rem;
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
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
</style>
