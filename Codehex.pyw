import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
import re

class CodeHexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CodeHex - Hex/Text Editor")
        self.root.geometry("800x600")
        
        # Make the background slightly transparent
        self.root.attributes("-alpha", 0.95)

        # Default to dark mode
        self.dark_mode = True

        # Text widget - monospaced font like Notepad
        self.text = tk.Text(self.root, wrap="none", font=("Courier", 10), bg="#1e1e1e", fg="white", insertbackground="white")
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a canvas for line numbers
        self.line_number_canvas = tk.Canvas(self.root, width=50, bg="#2e2e2e")
        self.line_number_canvas.pack(side=tk.LEFT, fill=tk.Y)

        # Bind key release event to update status
        self.text.bind("<KeyRelease>", self.update_status_bar)
        self.text.bind("<Configure>", self.update_line_numbers)
        
        # Menu setup
        self.menu_bar = tk.Menu(self.root, bg="lightgray", fg="black")
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, bg="lightgray", fg="black")
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Save As", command=self.save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Dark/Light Mode toggle
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0, bg="lightgray", fg="black")
        self.view_menu.add_command(label="Toggle Dark/Light Mode", command=self.toggle_mode)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)

        # Adding Edit menu like Notepad
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0, bg="lightgray", fg="black")
        self.edit_menu.add_command(label="Undo", command=self.undo)
        self.edit_menu.add_command(label="Redo", command=self.redo)
        self.edit_menu.add_command(label="Cut")
        self.edit_menu.add_command(label="Copy")
        self.edit_menu.add_command(label="Paste")
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        self.root.config(menu=self.menu_bar)

        # Status bar setup
        self.status_bar = tk.Label(self.root, text="Char: 0 | Line: 1 | UTC: 0", bd=1, relief=tk.SUNKEN, anchor="w")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.current_file = None
        self.update_text_color()

        # Update UTC time every second
        self.update_utc_time()

    def toggle_mode(self):
        """Switch between dark and light modes."""
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.root.config(bg="#2e2e2e")
            self.text.config(bg="#1e1e1e", fg="white", insertbackground="white")
            self.line_number_canvas.config(bg="#2e2e2e")
            self.status_bar.config(bg="#2e2e2e", fg="white")
        else:
            self.root.config(bg="white")
            self.text.config(bg="white", fg="black", insertbackground="black")
            self.line_number_canvas.config(bg="white")
            self.status_bar.config(bg="white", fg="black")

        self.update_text_color()  # Update text color when mode is toggled

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".*", filetypes=[("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, "rb") as file:
                    file_content = file.read()
                    if self.is_binary(file_content):
                        hex_content = file_content.hex()
                        self.text.delete(1.0, tk.END)
                        self.text.insert(tk.END, hex_content)
                    else:
                        decoded = file_content.decode("utf-8", errors="replace")
                        self.text.delete(1.0, tk.END)
                        self.text.insert(tk.END, decoded)

                self.current_file = file_path
                self.update_text_color()

            except Exception as e:
                messagebox.showerror("Error", f"Cannot open file: {e}")

    def save_file(self):
        if self.current_file:
            self._write_to_file(self.current_file)
        else:
            self.save_as()

    def save_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".*", filetypes=[("All Files", "*.*")])
        if file_path:
            self._write_to_file(file_path)
            self.current_file = file_path
            self.update_text_color()

    def _write_to_file(self, path):
        content = self.text.get(1.0, tk.END).strip()
        try:
            if path.lower().endswith((".exe", ".dll")):
                data = bytes.fromhex(content)
                with open(path, "wb") as f:
                    f.write(data)
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def is_binary(self, byte_data):
        """Detect binary file by checking for non-text bytes."""
        printable_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
        for byte in byte_data:
            if byte not in printable_chars:
                return True
        return False

    def update_text_color(self):
        """Update the text color based on the file type or status."""
        if self.current_file is None:
            self.text.config(fg="gray")  # Gray for unsaved
        else:
            ext = os.path.splitext(self.current_file)[1].lower()
            if ext in [".exe", ".dll"]:
                self.text.config(fg="red")  # Binary
            else:
                self.text.config(fg="black" if not self.dark_mode else "white")  # Text files

        self.update_status_bar()

    def update_line_numbers(self, event=None):
        """Update the line numbers based on the text content."""
        self.line_number_canvas.delete("all")
        
        lines = int(self.text.index("end-1c").split('.')[0])
        for i in range(1, lines+1):
            self.line_number_canvas.create_text(25, i*15, text=str(i), fill="white" if self.dark_mode else "black")

    def undo(self):
        """Undo the last action."""
        self.text.edit_undo()

    def redo(self):
        """Redo the last undone action."""
        self.text.edit_redo()

    def search(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("Search")
        
        # Search input field
        search_label = tk.Label(search_window, text="Find:")
        search_label.pack(pady=5)
        search_entry = tk.Entry(search_window, width=40)
        search_entry.pack(pady=5)
        
        def find_text():
            query = search_entry.get()
            if query:
                start = "1.0"
                while True:
                    start = self.text.search(query, start, stopindex=tk.END)
                    if not start:
                        break
                    end = f"{start}+{len(query)}c"
                    self.text.tag_add("highlight", start, end)
                    self.text.tag_configure("highlight", background="yellow")
                    start = end

        search_button = tk.Button(search_window, text="Find", command=find_text)
        search_button.pack(pady=5)

        search_window.mainloop()

    def highlight_syntax(self):
        """Simple Python syntax highlighting."""
        keywords = ['def', 'class', 'import', 'return']
        
        # Clear existing tags
        self.text.tag_remove('keyword', '1.0', tk.END)

        # Highlight keywords
        for keyword in keywords:
            start = "1.0"
            while True:
                start = self.text.search(r'\b' + keyword + r'\b', start, stopindex=tk.END)
                if not start:
                    break
                end = f"{start}+{len(keyword)}c"
                self.text.tag_add('keyword', start, end)
                self.text.tag_configure('keyword', foreground='blue')
                start = end

    def update_utc_time(self):
        """Update UTC time every second."""
        utc_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        self.status_bar.config(text=f"Char: {len(self.text.get(1.0, tk.END).replace('\n', ''))} | Line: {self.text.index('end-1c').split('.')[0]} | UTC: {utc_time}")
        self.root.after(1000, self.update_utc_time)

def main():
    root = tk.Tk()
    app = CodeHexApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()