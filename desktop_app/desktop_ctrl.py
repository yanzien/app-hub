# desktop_ctrl.py
# 真实桌面图标操控：通过 Windows API 找到桌面 ListView 并读写图标坐标
import ctypes
from ctypes import wintypes
import win32gui
import win32con

user32 = ctypes.windll.user32
LVF = 0x1000
LVM_GETITEMCOUNT    = LVF + 4
LVM_GETITEMPOSITION = LVF + 16
LVM_SETITEMPOSITION = LVF + 15
LVM_SETITEMPOSITION32 = LVF + 49
LVM_GETITEMTEXTW    = LVF + 45   # LVM_FIRST+45
LVM_GETITEMW        = LVF + 47   # LVM_FIRST+47
LVIF_TEXT = 0x0001

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

_listview = None

def _candidate_listviews():
    """枚举所有可能是桌面图标的 SysListView32（WorkerW 或 ProgMan 下）"""
    progman = win32gui.FindWindow("ProgMan", None)
    if progman:
        # 让 WorkerW 托管真正的桌面 ListView（多显示器/刷新后需要）
        win32gui.SendMessageTimeout(progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000)
    cands = []
    def enum(w, _):
        if win32gui.GetClassName(w) in ("WorkerW", "ProgMan"):
            shell = win32gui.FindWindowEx(w, None, "SHELLDLL_DefView", None)
            if shell:
                lv = win32gui.FindWindowEx(shell, None, "SysListView32", None)
                if lv:
                    cands.append((w, lv))
    win32gui.EnumWindows(enum, None)
    return progman, cands

def get_listview():
    global _listview
    if _listview and win32gui.IsWindow(_listview):
        return _listview
    for _ in range(6):
        progman, cands = _candidate_listviews()
        for w, lv in cands:
            if _readable(lv):
                _listview = lv
                return lv
        import time
        time.sleep(0.12)
    _, cands = _candidate_listviews()
    if cands:
        _listview = cands[0][1]
        return _listview
    return None

def _readable(lv):
    try:
        n = user32.SendMessageW(lv, LVM_GETITEMCOUNT, 0, 0)
        if n <= 0:
            return False
        p = POINT()
        user32.SendMessageW(lv, LVM_GETITEMPOSITION, 0, ctypes.byref(p))
        return True
    except Exception:
        return False

def icon_count():
    lv = get_listview()
    if not lv:
        return 0
    return user32.SendMessageW(lv, LVM_GETITEMCOUNT, 0, 0)

def get_positions():
    """返回 [(x, y), ...] 按图标索引顺序"""
    lv = get_listview()
    if not lv:
        return []
    n = icon_count()
    out = []
    for i in range(n):
        p = POINT()
        user32.SendMessageW(lv, LVM_GETITEMPOSITION, i, ctypes.byref(p))
        out.append((p.x, p.y))
    return out

def set_position(i, x, y):
    lv = get_listview()
    if not lv:
        return
    p = POINT(int(x), int(y))
    user32.SendMessageW(lv, LVM_SETITEMPOSITION32, i, ctypes.byref(p))

def set_positions(arr):
    """arr: [(x,y), ...]"""
    lv = get_listview()
    if not lv:
        return
    for i, (x, y) in enumerate(arr):
        p = POINT(int(x), int(y))
        user32.SendMessageW(lv, LVM_SETITEMPOSITION32, i, ctypes.byref(p))
    # 触发重绘
    user32.InvalidateRect(lv, None, True)

def get_labels():
    """返回图标文本列表（用于展示/调试）"""
    lv = get_listview()
    if not lv:
        return []
    n = icon_count()
    labels = []
    # LVITEMW 结构
    class LVITEMW(ctypes.Structure):
        _fields_ = [
            ("mask", wintypes.UINT),
            ("iItem", wintypes.INT),
            ("iSubItem", wintypes.INT),
            ("state", wintypes.UINT),
            ("stateMask", wintypes.UINT),
            ("pszText", ctypes.c_wchar_p),
            ("cchTextMax", wintypes.INT),
            ("iImage", wintypes.INT),
            ("lParam", wintypes.LPARAM),
            ("iIndent", wintypes.INT),
            ("iGroupId", wintypes.INT),
            ("cColumns", wintypes.UINT),
            ("puColumns", wintypes.PUINT),
            ("piColFmt", ctypes.c_void_p),
            ("iGroup", wintypes.INT),
        ]
    MAX = 260
    buf = ctypes.create_unicode_buffer(MAX)
    for i in range(n):
        item = LVITEMW()
        item.mask = LVIF_TEXT
        item.iItem = i
        item.iSubItem = 0
        item.pszText = ctypes.addressof(buf)
        item.cchTextMax = MAX
        user32.SendMessageW(lv, LVM_GETITEMTEXTW, i, ctypes.byref(item))
        labels.append(buf.value)
    return labels

def screen_size():
    return (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))

if __name__ == "__main__":
    print("listview:", get_listview())
    print("count:", icon_count())
    print("labels:", get_labels()[:5])
    print("pos0:", get_positions()[:3])
