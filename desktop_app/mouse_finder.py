# mouse_finder.py
# 真实跟随鼠标的箭头覆盖窗（pywin32 原生透明置顶窗）
# V2：用纯 Unicode 字符 + 简化窗口模型，确保可见
import win32gui, win32con, win32api, win32process
import ctypes
from ctypes import wintypes
import threading
import time
import os

user32 = ctypes.windll.user32

# 用一个绝对可靠的 Unicode 箭头字符
ARROW_CHAR = "\u25B2"  # ▲ 实心向上三角，所有字体都有
ARROW_FONT_SIZE = 36
WIN_W = 48
WIN_H = 52


class MouseFinder:
    def __init__(self):
        self.hwnd = None
        self.running = False
        self.thread = None
        self._font = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        # 注册简单窗口类
        wc_name = "MouseFinderV2_" + str(os.getpid())
        wc = wintypes.WNDCLASSW()
        wc.lpfnWndProc = win32gui.WndProcType(self._wnd_proc)
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = wc_name
        wc.hbrBackground = win32gui.GetStockObject(win32con.BLACK_BRUSH)
        try:
            win32gui.RegisterClass(wc)
        except Exception:
            pass

        # 创建置顶透明窗口
        style = win32con.WS_POPUP | win32con.WS_VISIBLE
        exstyle = (win32con.WS_EX_LAYERED |
                   win32con.WS_EX_TOOLWINDOW |
                   win32con.WS_EX_TOPMOST |
                   win32con.WS_EX_NOACTIVATE)

        self.hwnd = win32gui.CreateWindowEx(
            exstyle, wc_name, "",
            style, 0, 0, WIN_W, WIN_H,
            0, 0, win32api.GetModuleHandle(None), None
        )

        # 黑色全透明
        user32.SetLayeredWindowAttributes(
            self.hwnd, 0x000000, 255, win32con.LWA_COLORKEY
        )

        # 创建字体
        self._font = win32gui.CreateFont(
            ARROW_FONT_SIZE, 0, 0, 0, win32con.FW_BOLD,
            False, False, False, DEFAULT_CHARSET,
            OUT_OUTLINE_PRECIS, CLIP_DEFAULT_PRECIS,
            CLEARTYPE_QUALITY, VARIABLE_PITCH | FF_SWISS,
            "Segoe UI Symbol"
        )

        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

        # 跟随循环
        while self.running:
            try:
                x, y = win32api.GetCursorPos()
                # 放在鼠标右下方，稍微偏移
                tx = x + 24
                ty = y + 28
                win32gui.SetWindowPos(
                    self.hwnd, win32con.HWND_TOPMOST,
                    tx, ty, WIN_W, WIN_H,
                    win32con.SWP_NOACTIVATE | win32con.SWP_NOZORDER
                )
                # 强制重绘（确保箭头始终可见）
                win32gui.InvalidateRect(self.hwnd, None, True)
            except Exception:
                pass
            time.sleep(0.03)  # ~33fps

        # 清理
        if self.hwnd:
            try:
                win32gui.DestroyWindow(self.hwnd)
            except Exception:
                pass
            self.hwnd = None
        if self._font:
            try:
                win32gui.DeleteObject(self._font)
            except Exception:
                pass

    def _wnd_proc(self, hwnd, msg, wParam, lParam):
        if msg == win32con.WM_PAINT:
            hdc, ps = win32gui.BeginPaint(hwnd)
            try:
                # 设置背景模式为透明
                win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
                # 设置红色文字颜色
                win32gui.SetTextColor(hdc, 0xFF0000)  # 红色 BGR

                # 选入字体
                if self._font:
                    old_font = win32gui.SelectObject(hdc, self._font)

                # 绘制箭头文字（居中）
                rect = (4, 0, WIN_W - 4, WIN_H)
                win32gui.DrawText(
                    hdc, ARROW_CHAR, -1, rect,
                    win32con.DT_CENTER | win32con.DT_VCENTER | win32con.DT_SINGLELINE
                )

                # 恢复字体
                if self._font:
                    win32gui.SelectObject(hdc, old_font)
            finally:
                win32gui.EndPaint(hwnd, ps)
            return 0

        elif msg == win32con.WM_ERASEBKGND:
            # 用黑色填充背景（会被设为透明色）
            hdc = wParam
            rect = wintypes.RECT()
            user32.GetClientRect(hwnd, ctypes.byref(rect))
            brush = win32gui.GetStockObject(win32con.BLACK_BRUSH)
            win32gui.FillRect(hdc, ctypes.byref(rect), brush)
            return 1  # 已处理，不再默认擦除

        return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)

    def stop(self):
        self.running = False


# 常量
DEFAULT_CHARSET = 1
OUT_OUTLINE_PRECIS = 8
CLIP_DEFAULT_PRECIS = 0
CLEARTYPE_QUALITY = 5
VARIABLE_PITCH = 2
FF_SWISS = 36
