import { Editor } from "@tiptap/core";
import { StarterKit } from "@tiptap/starter-kit";

const editor = new Editor({
  element: document.querySelector("#editor-container"),
  extensions: [
    StarterKit,
    // Add other Tiptap extensions as needed
  ],
  content: "", // Initial content (you'll load it from Flask)
  onUpdate({ editor }) {
    // Save content to Flask whenever the editor changes
    fetch("/save_content", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(editor.getJSON()),
    });
  },
});

// Load initial content from Flask
fetch("/load_content")
  .then((response) => response.json())
  .then((data) => {
    editor.commands.setContent(data);
  });
