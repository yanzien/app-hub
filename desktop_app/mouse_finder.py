# mouse_finder.py
# 真实跟随鼠标的箭头覆盖窗（tkinter 置顶透明窗）
import tkinter as tk
import threading
import win32api

class MouseFinder:
    def __init__(self):
        self.root = None
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-transparentcolor", "white")
        self.root.configure(bg="white")
        lbl = tk.Label(self.root, text="👆", font=("Segoe UI Emoji", 42),
                       fg="#ff3b3b", bg="white")
        lbl.pack()
        self.root.geometry("64x64+0+0")
        self._follow()
        self.root.mainloop()

    def _follow(self):
        if not self.running or not self.root:
            if self.root:
                try:
                    self.root.destroy()
                except Exception:
                    pass
            return
        try:
            x, y = win32api.GetCursorPos()
        except Exception:
            x, y = 0, 0
        self.root.geometry(f"64x64+{x + 34}+{y + 34}")
        self.root.after(16, self._follow)

    def stop(self):
        self.running = False
        if self.root:
            try:
                self.root.destroy()
            except Exception:
                pass
        self.root = None
