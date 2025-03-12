import tkinter as tk
from tkinter import messagebox, Frame, Entry
from tkinterdnd2 import DND_FILES, TkinterDnD
import subprocess
import os
import threading
import pickle
import queue
import signal

SCRIPTS_FILE = 'stored_scripts.pkl'

class PythonRunnerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Script Runner")
        self.root.geometry("600x400")
        self.root.configure(bg='black')

        self.label = tk.Label(root, text="Drag and drop your file here", fg='white', bg='black')
        self.label.pack(pady=20)

        # Canvas to display scripts and delete buttons
        self.canvas_frame = Frame(root, bg='black')
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(self.canvas_frame, bg='black', width=580, height=300)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.canvas_frame, bg='black', troughcolor='black', activebackground='black', command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.inner_frame = Frame(self.canvas, bg='black')
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Enable drag and drop
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

        # Load stored scripts
        self.scripts = self.load_scripts()
        self.processes = {}  # Dictionary to keep track of running processes
        self.update_script_list()

        # Run stored scripts on startup
        self.run_stored_scripts()

        # Queue for thread-safe messagebox calls
        self.message_queue = queue.Queue()
        self.root.after(100, self.process_message_queue)

    def on_drop(self, event):
        file_path = event.data.strip('{}')
        if file_path.endswith('.py'):
            self.add_script(file_path)
        else:
            self.message_queue.put(("error", "Please drop a valid Python file."))

    def add_script(self, file_path):
        custom_name = os.path.basename(file_path)
        if file_path not in [s[0] for s in self.scripts]:
            self.scripts.append((file_path, custom_name))
            self.save_scripts()
            self.update_script_list()
            self.run_script(file_path)

    def remove_script(self, file_path):
        self.scripts = [s for s in self.scripts if s[0] != file_path]
        self.save_scripts()
        self.update_script_list()
        self.stop_script(file_path)

    def run_script(self, file_path):
        def execute_script():
            try:
                process = subprocess.Popen(['python3', file_path])
                self.processes[file_path] = process
                self.message_queue.put(("info", f"Script {os.path.basename(file_path)} is running in the background."))
            except Exception as e:
                self.message_queue.put(("error", f"Failed to run script: {e}"))

        thread = threading.Thread(target=execute_script)
        thread.start()

    def stop_script(self, file_path):
        if file_path in self.processes:
            process = self.processes.pop(file_path)
            try:
                os.kill(process.pid, signal.SIGTERM)
                self.message_queue.put(("info", f"Script {os.path.basename(file_path)} has been stopped."))
            except Exception as e:
                self.message_queue.put(("error", f"Failed to stop script: {e}"))

    def run_stored_scripts(self):
        for script, _ in self.scripts:
            self.run_script(script)

    def load_scripts(self):
        if os.path.exists(SCRIPTS_FILE):
            with open(SCRIPTS_FILE, 'rb') as file:
                scripts = pickle.load(file)
                # Ensure scripts are in the correct format
                if all(isinstance(s, tuple) and len(s) == 2 for s in scripts):
                    return scripts
                else:
                    # Convert old format to new format
                    return [(s, os.path.basename(s)) for s in scripts]
        return []

    def save_scripts(self):
        with open(SCRIPTS_FILE, 'wb') as file:
            pickle.dump(self.scripts, file)

    def update_script_list(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        for script, custom_name in self.scripts:
            frame = Frame(self.inner_frame, bg='black')
            frame.pack(fill=tk.X, padx=5, pady=5)  # Added pady for space between lines

            # Entry for custom name
            entry = Entry(frame, fg='white', bg='black', width=30)
            entry.insert(0, custom_name)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Bind the Return event to save the custom name
            entry.bind("<Return>", lambda event, path=script: self.validate_custom_name(event, path))

            # Label for the file path, aligned to the right
            path_label = tk.Label(frame, text=script, fg='white', bg='black', anchor='e')
            path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Delete button, centered within its allocated space
            delete_button = tk.Button(frame, text="🗑", command=lambda path=script: self.remove_script(path), bg='black', padx=2, pady=2, highlightthickness=0)
            delete_button.pack(side=tk.RIGHT)

    def validate_custom_name(self, event, file_path):
        new_name = event.widget.get().strip()
        if new_name:  # Ensure the custom name is not empty
            self.scripts = [(s[0], new_name) if s[0] == file_path else s for s in self.scripts]
            self.save_scripts()
            self.root.focus()  # Remove focus from the entry field

    def process_message_queue(self):
        try:
            message_type, message = self.message_queue.get_nowait()
            if message_type == "info":
                messagebox.showinfo("Success", message)
            elif message_type == "error":
                messagebox.showerror("Error", message)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_message_queue)

if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Use TkinterDnD instead of tk.Tk
    app = PythonRunnerApp(root)
    root.mainloop()
