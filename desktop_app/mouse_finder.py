# mouse_finder.py
# 真实跟随鼠标的箭头覆盖窗（pywin32 原生透明置顶窗，无需 tkinter）
import win32gui, win32con, win32api
import ctypes
from ctypes import wintypes
import threading
import time

user32 = ctypes.windll.user32

# 箭头窗口类名
WC_ARROW = "MouseFinderArrow_2026"

def _register_class():
    """注册窗口类（仅一次）"""
    wc = wintypes.WNDCLASSW()
    wc.lpfnWndProc = win32gui.WndProcType(_wnd_proc)
    wc.hInstance = win32api.GetModuleHandle(None)
    wc.lpszClassName = WC_ARROW
    wc.hbrBackground = None  # 透明背景
    try:
        win32gui.RegisterClass(wc)
    except Exception:
        pass  # 已注册则忽略

def _wnd_proc(hwnd, msg, wParam, lParam):
    """最小窗口过程——只处理关闭和绘制"""
    if msg == win32con.WM_DESTROY:
        win32gui.PostQuitMessage(0)
        return 0
    elif msg == win32con.WM_PAINT:
        # 用 GDI 绘制箭头文字
        hdc, ps = win32gui.BeginPaint(hwnd)
        try:
            # 设置透明模式 + 文字
            win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
            # 红色粗体大字
            hfont = win32gui.LOGFONT()
            hfont.lfHeight = 42
            hfont.lfWeight = win32con.FW_BOLD
            hfont.lfFaceName = "Segoe UI Emoji"
            font = win32gui.CreateFontIndirect(hfont)
            old = win32gui.SelectObject(hdc, font)
            win32gui.SetTextColor(hdc, 0xFF3B3B)  # 红色
            win32gui.TextOut(hdc, 4, 0, "\u{1F446}", 2)  # 👆
            win32gui.SelectObject(hdc, old)
            win32gui.DeleteObject(font)
        finally:
            win32gui.EndPaint(hwnd, ps)
        return 0
    return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)


class MouseFinder:
    def __init__(self):
        self.hwnd = None
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        _register_class()
        style = (win32con.WS_POPUP |
                 win32con.WS_VISIBLE |
                 win32con.WS_DISABLED)  # 不接收鼠标事件
        exstyle = (win32con.WS_EX_LAYERED |
                   win32con.WS_EX_TOOLWINDOW |   # 不在任务栏显示
                   win32con.WS_EX_TOPMOST |       # 置顶
                   win32con.WS_EX_TRANSPARENT)    # 鼠标穿透

        # 创建 64x64 透明窗口
        self.hwnd = win32gui.CreateWindowEx(
            exstyle, WC_ARROW, "",
            style, 0, 0, 64, 64,
            0, 0, win32api.GetModuleHandle(None), None
        )

        # 设透明色（白色=透明）
        user32.SetLayeredWindowAttributes(self.hwnd, 0xFFFFFF, 255, win32con.LWA_COLORKEY)

        # 显示
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

        # 跟随循环
        while self.running:
            try:
                x, y = win32api.GetCursorPos()
                # 窗口中心对准鼠标右下方
                win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST,
                                      x + 34, y + 34, 64, 64,
                                      win32con.SWP_NOACTIVATE)
            except Exception:
                pass
            time.sleep(0.016)  # ~60fps

        # 清理
        if self.hwnd:
            try:
                win32gui.DestroyWindow(self.hwnd)
            except Exception:
                pass
            self.hwnd = None

    def stop(self):
        self.running = False
        # 线程会在下次循环检查时退出并清理窗口
