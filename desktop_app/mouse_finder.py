# mouse_finder.py
# 真实跟随鼠标的箭头覆盖窗（pywin32 原生透明置顶窗，无需 tkinter）
# 用 GDI 多边形绘制箭头（不依赖 emoji 字体渲染）
import win32gui, win32con, win32api
import ctypes
from ctypes import wintypes
import threading
import time

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

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

def _draw_arrow(hdc, w, h):
    """用 GDI 绘制一个红色箭头（多边形 + 线条，不依赖字体）"""
    # 红色画笔 + 红色刷子
    pen = gdi32.CreatePen(win32con.PS_SOLID, 3, 0x0000FF)  # 红色 RGB
    brush = gdi32.CreateSolidBrush(0x0000FF)
    old_pen = gdi32.SelectObject(hdc, pen)
    old_brush = gdi32.SelectObject(hdc, brush)

    # 设置混合模式（透明背景）
    gdi32.SetBkMode(hdc, win32con.TRANSPARENT)

    cx, cy = w // 2, h // 2

    # 箭头三角形（指向上方偏右）
    points = (
        wintypes.POINT(cx, 4),           # 顶点
        wintypes.POINT(4, h - 6),        # 左下
        wintypes.POINT(cx + 4, h - 16),   # 内凹底中
        wintypes.POINT(w - 4, h - 6),     # 右下
    )
    gdi32.Polygon(hdc, points, len(points))

    # 箭头杆子（从三角形底部向下延伸一小段）
    gdi32.MoveToEx(hdc, cx, h - 14, None)
    gdi32.LineTo(hdc, cx, h - 2)

    # 清理
    gdi32.SelectObject(hdc, old_pen)
    gdi32.SelectObject(hdc, old_brush)
    gdi32.DeleteObject(pen)
    gdi32.DeleteObject(brush)


def _wnd_proc(hwnd, msg, wParam, lParam):
    """窗口过程"""
    if msg == win32con.WM_DESTROY:
        win32gui.PostQuitMessage(0)
        return 0
    elif msg == win32con.WM_PAINT:
        hdc, ps = win32gui.BeginPaint(hwnd)
        try:
            rect = wintypes.RECT()
            user32.GetClientRect(hwnd, ctypes.byref(rect))
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            _draw_arrow(hdc, w, h)
        finally:
            win32gui.EndPaint(hwnd, ps)
        return 0
    elif msg == win32con.WM_ERASEBKGND:
        return 1  # 不擦除背景（保持透明）
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

        # 创建 48x48 透明窗口
        self.hwnd = win32gui.CreateWindowEx(
            exstyle, WC_ARROW, "",
            style, 0, 0, 48, 48,
            0, 0, win32api.GetModuleHandle(None), None
        )

        # 设透明色（黑色=透明）
        user32.SetLayeredWindowAttributes(self.hwnd, 0x000000, 255, win32con.LWA_COLORKEY)

        # 显示
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

        # 跟随循环
        while self.running:
            try:
                x, y = win32api.GetCursorPos()
                # 窗口放在鼠标右下方
                win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST,
                                      x + 28, y + 28, 48, 48,
                                      win32con.SWP_NOACTIVATE)
            except Exception:
                pass
            time.sleep(0.02)  # ~50fps

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
