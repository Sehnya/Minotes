import { createApp } from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js'
import { Editor, EditorContent } from 'https://esm.sh/@tiptap/vue-3@2'
import StarterKit from 'https://esm.sh/@tiptap/starter-kit@2'

createApp({
  components: { EditorContent },
  data() {
    return {
      editor: null,
    }
  },
  mounted() {
    this.editor = new Editor({
      content: '<p>Start typing your note...</p>',
      extensions: [StarterKit],
      onUpdate: ({ editor }) => {
        const html = editor.getHTML()
        document.getElementById('editor-content').value = html
      },
    })
  },
  beforeUnmount() {
    this.editor?.destroy()
  },
  template: `<EditorContent :editor="editor" />`
}).mount('#editor')
