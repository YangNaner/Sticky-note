import customtkinter as ctk
from sticky_note import StickyNote
import json
import os
import sys
from tkinter import mainloop
import threading
import portalocker

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".sticky_notes")
CONFIG_FILE = os.path.join(CONFIG_DIR, "notes.json")
LOCK_FILE = os.path.join(CONFIG_DIR, ".lock")

notes = []
app = None
is_hidden = False
tray_icon = None
lock_file = None

def check_single_instance():
    global lock_file
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        lock_file = open(LOCK_FILE, 'w')
        portalocker.lock(lock_file, portalocker.LOCK_EX | portalocker.LOCK_NB)
        lock_file.write(str(os.getpid()))
        return True
    except (IOError, OSError, portalocker.exceptions.AlreadyLocked):
        return False

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
            "width": note.winfo_width(),
            "height": note.winfo_height(),
            "content": note.text_area.get("1.0", "end-1c")
        })
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(notes_data, f, ensure_ascii=False, indent=2)

def create_note_in_main(x=100, y=100, width=250, height=300, content=""):
    note = StickyNote(x=x, y=y, width=width, height=height, content=content)
    notes.append(note)

    def on_destroy_callback(n):
        notes.remove(n)
        save_notes()

    def on_create_note_callback(n):
        def do_create():
            add_note_to_main()
        app.after(0, do_create)

    note.on_destroy_callback = on_destroy_callback
    note.on_create_note_callback = on_create_note_callback
    note.on_close_callback = on_closing

    return note

def add_note_to_main():
    if notes:
        # 已有便签，出现在最左上方便签的左上方
        min_x = min(n.winfo_x() for n in notes)
        min_y = min(n.winfo_y() for n in notes)
        create_note_in_main(x=min_x - 30, y=min_y - 30)
    else:
        # 没有便签，出现在屏幕右下角
        import screeninfo
        monitor = screeninfo.get_monitors()[0]
        x = monitor.x + monitor.width - 300
        y = monitor.y + monitor.height - 350
        create_note_in_main(x=x, y=y)

def create_note(x=100, y=100, width=250, height=300, content=""):
    return create_note_in_main(x, y, width, height, content)

def on_closing():
    save_notes()
    for note in notes:
        note.destroy()
    if lock_file:
        try:
            portalocker.unlock(lock_file)
            lock_file.close()
            os.remove(LOCK_FILE)
        except:
            pass
    sys.exit()

def show_notification(title, message):
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)
    except Exception as e:
        pass

def setup_tray():
    from pystray import Icon, Menu, MenuItem
    import PIL.Image

    def create_image():
        import sys
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return PIL.Image.open(os.path.join(base_path, "logo.ico"))

    def get_menu():
        global is_hidden
        check = " ✓" if is_hidden else ""
        return Menu(
            MenuItem("新建便签", add_note),
            MenuItem("展示", show_all),
            MenuItem(f"隐藏{check}", toggle_hide),
            MenuItem("关闭", quit_app)
        )

    def show_all(icon, item):
        if app:
            app.after(0, bring_all_to_front)

    def add_note(icon, item):
        if app:
            app.after(0, add_note_to_main)

    def toggle_hide(icon, item):
        global is_hidden, tray_icon
        is_hidden = not is_hidden
        if app:
            if is_hidden:
                app.after(0, lambda: [note.withdraw() for note in notes])
            else:
                app.after(0, lambda: [note.deiconify() for note in notes])
        tray_icon.menu = get_menu()

    def quit_app(icon, item):
        if app:
            def do_quit():
                save_notes()
                for note in notes:
                    note.destroy()
                if lock_file:
                    try:
                        portalocker.unlock(lock_file)
                        lock_file.close()
                        os.remove(LOCK_FILE)
                    except:
                        pass
                os._exit(0)
            app.after(0, do_quit)

    menu = get_menu()

    global tray_icon
    tray_icon = Icon("sticky_notes", create_image(), "便利贴", menu)

    def send_notify():
        import time
        time.sleep(0.5)
        show_notification("Sticky-note", "便利贴已启动")

    notify_thread = threading.Thread(target=send_notify, daemon=True)
    notify_thread.start()

    tray_icon.run()

def bring_all_to_front():
    for note in notes:
        note.wm_attributes("-topmost", True)
        note.lift()
        note.wm_attributes("-topmost", False)

def main():
    global app
    if not check_single_instance():
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, "程序已在运行", "Sticky-note", 0x40)
        sys.exit()

    app = ctk.CTk()
    app.withdraw()

    ctk.set_appearance_mode("light")

    tray_thread = threading.Thread(target=setup_tray, daemon=True)
    tray_thread.start()

    # 等待托盘初始化
    import time
    time.sleep(0.5)

    notes_data = load_notes()

    if notes_data:
        for data in notes_data:
            create_note(
                x=data.get("x", 100),
                y=data.get("y", 100),
                width=data.get("width", 250),
                height=data.get("height", 300),
                content=data.get("content", "")
            )

    mainloop()

if __name__ == "__main__":
    main()
