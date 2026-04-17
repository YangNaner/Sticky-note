import customtkinter as ctk
from sticky_note import StickyNote
import json
import os
import sys
from tkinter import mainloop
import threading

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".sticky_notes")
CONFIG_FILE = os.path.join(CONFIG_DIR, "notes.json")

notes = []
app = None

def load_notes():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_notes():
    notes_data = []
    for note in notes:
        notes_data.append({
            "x": note.winfo_x(),
            "y": note.winfo_y(),
            "content": note.text_area.get("1.0", "end-1c")
        })
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(notes_data, f, ensure_ascii=False, indent=2)

def create_note(x=100, y=100, content=""):
    note = StickyNote(x=x, y=y, content=content)
    notes.append(note)
    return note

def on_closing():
    save_notes()
    for note in notes:
        note.destroy()
    sys.exit()

def setup_tray():
    from pystray import Icon, Menu, MenuItem
    import PIL.Image

    def create_image():
        img = PIL.Image.new('RGB', (64, 64), color='#FFE866')
        return img

    def show_window(icon, item):
        if app:
            app.after(0, lambda: [note.deiconify() for note in notes])

    def hide_window(icon, item):
        if app:
            app.after(0, lambda: [note.withdraw() for note in notes])

    def add_note(icon, item):
        if app:
            def do_add():
                create_note(x=200, y=200)
                if notes:
                    def on_note_close(n=notes[-1]):
                        notes.remove(n)
                        n.destroy()
                        if not notes:
                            save_notes()
                            os._exit(0)
                    notes[-1].on_close_callback = on_note_close
            app.after(0, do_add)

    def quit_app(icon, item):
        if app:
            app.after(0, lambda: (save_notes(), [note.destroy() for note in notes], os._exit(0)))

    menu = Menu(
        MenuItem("显示", show_window),
        MenuItem("隐藏", hide_window),
        MenuItem("新建便签", add_note),
        MenuItem("退出", quit_app)
    )

    icon = Icon("sticky_notes", create_image(), "便利贴", menu)
    icon.run()

def main():
    global app
    app = ctk.CTk()
    app.withdraw()

    ctk.set_appearance_mode("light")

    tray_thread = threading.Thread(target=setup_tray, daemon=True)
    tray_thread.start()

    notes_data = load_notes()

    if notes_data:
        for data in notes_data:
            create_note(
                x=data.get("x", 100),
                y=data.get("y", 100),
                content=data.get("content", "")
            )
    else:
        create_note(x=100, y=100)

    for note in notes:
        note.on_close_callback = on_closing

    mainloop()

if __name__ == "__main__":
    main()
