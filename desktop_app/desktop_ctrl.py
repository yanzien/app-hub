# desktop_ctrl.py
# 真实桌面图标操控：通过 Windows API 找到桌面 ListView 并读写图标坐标
# 兼容 Win10 / Win11 多显示器 / 不同 shell 配置
import ctypes
from ctypes import wintypes
import win32gui
import win32con
import time

user32 = ctypes.windll.user32
LVF = 0x1000
LVM_GETITEMCOUNT    = LVF + 4
LVM_GETITEMPOSITION = LVF + 16
LVM_SETITEMPOSITION = LVF + 15
LVM_SETITEMPOSITION32 = LVF + 49

class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

_listview = None
_debug_log = []

def log(msg):
    _debug_log.append(msg)
    if len(_debug_log) > 50:
        _debug_log.pop(0)

def get_debug_log():
    return "\n".join(_debug_log)

def _find_listview_v1():
    """经典方法：ProgMan → WorkerW → SHELLDLL_DefView → SysListView32"""
    progman = win32gui.FindWindow("ProgMan", None)
    if not progman:
        log("V1: ProgMan not found")
        return None

    # 发送 0x052C 让 WorkerW 暴露桌面 ListView
    result = win32gui.SendMessageTimeout(progman, 0x052C, 0, 0,
                                         win32con.SMTO_NORMAL, 1000)
    log(f"V1: SendMessage 0x052C -> {result}")

    # 方法 A：直接从 ProgMan 找
    shell = win32gui.FindWindowEx(progman, None, "SHELLDLL_DefView", None)
    if shell:
        lv = win32gui.FindWindowEx(shell, None, "SysListView32", None)
        if lv:
            n = user32.SendMessageW(lv, LVM_GETITEMCOUNT, 0, 0)
            log(f"V1-A: Found via ProgMan direct, count={n}")
            if n > 0:
                return lv

    # 方法 B：枚举所有 WorkerW，找包含 SHELLDLL_DefView 的
    def enum_cb(w, _):
        cls = win32gui.GetClassName(w)
        if cls == "WorkerW":
            sh = win32gui.FindWindowEx(w, None, "SHELLDLL_DefView", None)
            if sh:
                lv = win32gui.FindWindowEx(sh, None, "SysListView32", None)
                if lv:
                    n = user32.SendMessageW(lv, LVM_GETITEMCOUNT, 0, 0)
                    vis = win32gui.IsWindowVisible(w) or win32gui.IsWindowVisible(lv)
                    log(f"V1-B: WorkerW={w} visible={vis} count={n}")
                    if n > 0:
                        return lv
        return None

    found = None
    def enum_wrapper(w, _):
        nonlocal found
        found = enum_cb(w, _)

    win32gui.EnumWindows(enum_wrapper, None)
    if found:
        return found

    log("V1: No usable ListView found")
    return None


def _find_listview_v2():
    """暴力方法：枚举所有窗口找任何有图标的 SysListView32"""
    results = []
    def enum_cb(w, _):
        try:
            cls = win32gui.GetClassName(w)
            if cls == "SysListView32":
                n = user32.SendMessageW(w, LVM_GETITEMCOUNT, 0, 0)
                # 检查父窗口链是否像桌面
                parent = win32gui.GetParent(w)
                grandparent = win32gui.GetParent(parent) if parent else 0
                p_cls = win32gui.GetClassName(parent) if parent else ""
                gp_cls = win32gui.GetClassName(grandparent) if grandparent else ""
                vis = win32gui.IsWindowVisible(w)
                log(f"V2: LV={w} parent={p_cls} gparent={gp_cls} visible={vis} count={n}")
                if n > 0:
                    # 优先选父窗口是 SHELLDLL_DefView 或 WorkerW 的
                    if p_cls in ("SHELLDLL_DefView", "WorkerW"):
                        results.insert(0, w)
                    else:
                        results.append(w)
        except Exception as e:
            log(f"V2: Error checking {w}: {e}")

    win32gui.EnumWindows(enum_cb, None)
    log(f"V2: Found {len(results)} candidate ListViews")
    return results[0] if results else None


def get_listview():
    global _listview
    if _listview and win32gui.IsWindow(_listview):
        # 验证还活着
        try:
            n = user32.SendMessageW(_listview, LVM_GETITEMCOUNT, 0, 0)
            if n > 0:
                return _listview
        except Exception:
            pass

    _debug_log.clear()

    # 尝试 V1（标准方法），重试几次
    for attempt in range(4):
        lv = _find_listview_v1()
        if lv:
            _listview = lv
            log(f"get_listview: V1 succeeded on attempt {attempt+1}")
            return lv
        time.sleep(0.15)

    # 尝试 V2（暴力枚举）
    lv = _find_listview_v2()
    if lv:
        _listview = lv
        log("get_listview: V2 succeeded")
        return lv

    log("get_listview: ALL methods failed")
    return None


def icon_count():
    lv = get_listview()
    if not lv:
        return 0
    try:
        return user32.SendMessageW(lv, LVM_GETITEMCOUNT, 0, 0)
    except Exception:
        return 0


def get_positions():
    """返回 [(x, y), ...] 按图标索引顺序"""
    lv = get_listview()
    if not lv:
        return []
    n = icon_count()
    if n <= 0:
        return []
    out = []
    for i in range(n):
        p = POINT()
        r = user32.SendMessageW(lv, LVM_GETITEMPOSITION, i, ctypes.byref(p))
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
    # 不再强制 InvalidateRect — 让 Windows 自然重绘，避免闪烁


def get_labels():
    """返回图标文本列表（用于展示/调试）"""
    lv = get_listview()
    if not lv:
        return []
    n = icon_count()
    if n <= 0:
        return []

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
            ("puColumns", ctypes.PUINT),
            ("piColFmt", ctypes.c_void_p),
            ("iGroup", wintypes.INT),
        ]

    MAX = 260
    buf = ctypes.create_unicode_buffer(MAX)
    labels = []
    for i in range(n):
        item = LVITEMW()
        item.mask = 0x0001  # LVIF_TEXT
        item.iItem = i
        item.iSubItem = 0
        item.pszText = ctypes.addressof(buf)
        item.cchTextMax = MAX
        user32.SendMessageW(lv, LVF + 45, i, ctypes.byref(item))  # LVM_GETITEMTEXTW
        labels.append(buf.value)
    return labels


def screen_size():
    return (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))


if __name__ == "__main__":
    print("=" * 50)
    lv = get_listview()
    print(f"ListView: {lv}")
    print(f"Icon count: {icon_count()}")
    pos = get_positions()
    print(f"Positions ({len(pos)}): {pos[:5]}")
    lbls = get_labels()
    print(f"Labels ({len(lbls)}): {lbls[:10]}")
    print(f"Screen: {screen_size()}")
    print("Debug log:")
    print(get_debug_log())
