const saveBtn = document.getElementById('save-btn') as HTMLButtonElement
const titleInput = document.getElementById('note-title') as HTMLInputElement
const contentInput = document.getElementById('note-content') as HTMLTextAreaElement
const noteList = document.getElementById('note-list') as HTMLUListElement

interface Note {
  title: string
  content: string
  id: number
}

async function fetchNotes(): Promise<void> {
  const res = await fetch('https://your-backend.onrender.com/api/notes', {
    credentials: 'include',
  })
  const data = await res.json()
  noteList.innerHTML = ''
  data.notes.forEach((note: Note) => {
    const li = document.createElement('li')
    li.innerHTML = `<strong>${note.title}</strong><p>${note.content}</p>`
    noteList.appendChild(li)
  })
}

saveBtn.addEventListener('click', async () => {
  const title = titleInput.value.trim()
  const content = contentInput.value.trim()

  if (!title || !content) return alert('Please enter title and content.')

  const res = await fetch('https://your-backend.onrender.com/save_note', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ title, content })
  })

  const data = await res.json()
  alert(data.message || 'Note saved.')
  await fetchNotes()
})
fetchNotes()
