const titleInput = document.getElementById('note-title') as HTMLInputElement
const contentInput = document.getElementById('note-content') as HTMLTextAreaElement
const saveBtn = document.getElementById('save-btn') as HTMLButtonElement
const noteList = document.getElementById('note-list') as HTMLUListElement

interface Note {
  id: number
  title: string
  content: string
}

async function checkSession(): Promise<void> {
  const res = await fetch('http://localhost:5000/api/session', {
    credentials: 'include'
  })

  if (!res.ok) {
    alert("Not logged in. Redirecting...")
    window.location.href = 'http://localhost:5000/login'
  }
}

async function loadNotes(): Promise<void> {
  const res = await fetch('http://localhost:5000/api/notes', {
    credentials: 'include'
  })

  const data = await res.json()
  const notes: Note[] = data.notes || []

  noteList.innerHTML = ''
  notes.forEach((note) => {
    const li = document.createElement('li')
    li.innerHTML = `<strong>${note.title}</strong><p>${note.content}</p>`
    noteList.appendChild(li)
  })
}

async function saveNote(): Promise<void> {
  const title = titleInput.value.trim()
  const content = contentInput.value.trim()

  if (!title || !content) {
    alert("Title and content are required.")
    return
  }

  const res = await fetch('http://localhost:5000/save_note', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ title, content })
  })

  const data = await res.json()
  alert(data.message || "Note saved.")

  titleInput.value = ''
  contentInput.value = ''
  await loadNotes()
}

saveBtn.addEventListener('click', saveNote)

checkSession()
loadNotes()