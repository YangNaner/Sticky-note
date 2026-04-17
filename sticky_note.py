import customtkinter as ctk
from tkinter import Menu as TkMenu

class StickyNote(ctk.CTk):
    def __init__(self, x=100, y=100, width=250, height=300, font_size=11, content=""):
        super().__init__()

        self.on_close_callback = None
        self.on_destroy_callback = None

        self.overrideredirect(True)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.configure(fg_color="#FFE866")
        self.wm_attributes("-topmost", False)

        self._font_size = font_size

        # 外层框架（深黄色边框）
        self.outer_frame = ctk.CTkFrame(
            self,
            fg_color="#FFE866",
            corner_radius=8,
            border_width=0
        )
        self.outer_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))

        # 拖动区域（顶部深黄色条，放置在外层框架内）
        self.drag_bar = ctk.CTkFrame(
            self.outer_frame,
            height=20,
            fg_color="#FFE866",
            corner_radius=0,
            border_width=0
        )
        self.drag_bar.pack(fill="x", padx=0, pady=(0, 0))
        self.drag_bar.pack_propagate(False)

        self.drag_bar.bind("<Button-1>", self.start_drag)
        self.drag_bar.bind("<B1-Motion>", self.drag)
        self.drag_bar.bind("<Button-3>", self.show_context_menu)
        self.drag_bar.bind("<Control-Button-1>", lambda e: self.toggle_topmost())

        # Esc 销毁便签
        self.bind("<KeyPress-Escape>", lambda e: self.destroy_note())

        # 文本输入区域（浅黄色，放置在外层框架内）
        self.text_area = ctk.CTkTextbox(
            self.outer_frame,
            font=("Microsoft YaHei", self._font_size),
            fg_color="#FFFACD",
            border_width=0,
            wrap="word"
        )
        self.text_area.pack(fill="both", expand=True, padx=2, pady=(3, 2))
        if content:
            self.text_area.insert("1.0", content)

        # 文本区域可以输入，不能拖动
        self.text_area.bind("<Button-1>", lambda e: self.text_area.focus_set())
        self.bind("<Button-1>", self.set_focused)

        # 全局释放停止拖动
        self.bind("<ButtonRelease-1>", self.stop_drag)
        self.text_area.bind("<MouseWheel>", self.on_mousewheel)

        self._dragging = False
        self._drag_x = 0
        self._drag_y = 0
        self._is_topmost = False
        self._focused = False

        # 右键菜单
        self.context_menu = TkMenu(self, tearoff=0, bg="white", bd=0)

        self.context_menu.add_command(label="新建便签", command=self.create_new_note, background="white")
        self.context_menu.add_separator()
        self.context_menu.add_command(label="销毁", command=self.destroy_note, background="white")
        self.context_menu.add_command(label="置顶 ○", command=self.toggle_topmost, background="white")

        self.update_idletasks()
        self.deiconify()

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def create_new_note(self):
        if hasattr(self, 'on_create_note_callback'):
            self.on_create_note_callback(self)

    def destroy_note(self):
        if self.on_destroy_callback:
            self.on_destroy_callback(self)
        self.destroy()

    def toggle_topmost(self):
        self._is_topmost = not self._is_topmost
        self.wm_attributes("-topmost", self._is_topmost)
        # 更新菜单文字
        check = " ✓" if self._is_topmost else " ○"
        self.context_menu.entryconfigure(3, label=f"置顶{check}")

    def start_drag(self, event):
        self._dragging = True
        self._drag_x = event.x
        self._drag_y = event.y

    def drag(self, event):
        if self._dragging:
            delta_x = event.x - self._drag_x
            delta_y = event.y - self._drag_y
            new_x = self.winfo_x() + delta_x
            new_y = self.winfo_y() + delta_y
            self.geometry(f"+{new_x}+{new_y}")

    def stop_drag(self, event):
        self._dragging = False

    def set_focused(self, event):
        self._focused = True

    def on_mousewheel(self, event):
        if self._focused:
            if event.state & 0x4:  # Ctrl key - 调整窗口大小
                current_width = self.winfo_width()
                delta = 30 if event.delta > 0 else -30
                new_width = max(200, min(800, current_width + delta))
                new_height = int(new_width * 6 / 5)
                new_height = max(240, min(960, new_height))
                self.geometry(f"{new_width}x{new_height}")
            elif event.state & 0x20000:  # Alt key - 调整字体大小，阻止冒泡
                delta = 2 if event.delta > 0 else -2
                self._font_size = max(8, min(24, self._font_size + delta))
                self.text_area.configure(font=("Microsoft YaHei", self._font_size))
                return "break"

    def close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()
