import customtkinter as ctk

class StickyNote(ctk.CTk):
    def __init__(self, x=100, y=100, content=""):
        super().__init__()

        self.on_close_callback = None

        self.overrideredirect(True)
        self.geometry(f"250x300+{x}+{y}")
        self.configure(fg_color="#FFE866")

        # 拖动区域（顶部深黄色条）
        self.drag_bar = ctk.CTkFrame(
            self,
            height=35,
            fg_color="#FFE866",
            corner_radius=0
        )
        self.drag_bar.pack(fill="x")
        self.drag_bar.pack_propagate(False)

        self.drag_bar.bind("<Button-1>", self.start_drag)
        self.drag_bar.bind("<B1-Motion>", self.drag)

        # 文本输入区域（浅黄色）
        self.text_area = ctk.CTkTextbox(
            self,
            font=("Microsoft YaHei", 11),
            fg_color="#FFFACD",
            border_width=0,
            wrap="word"
        )
        self.text_area.pack(fill="both", expand=True, padx=0, pady=0)
        if content:
            self.text_area.insert("1.0", content)

        # 文本区域可以输入，不能拖动
        self.text_area.bind("<Button-1>", lambda e: self.text_area.focus_set())

        # 全局释放停止拖动
        self.bind("<ButtonRelease-1>", self.stop_drag)

        self._dragging = False
        self._drag_x = 0
        self._drag_y = 0

        self.update_idletasks()
        self.deiconify()

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

    def close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()
