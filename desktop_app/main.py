# main.py
# 桌面操控器 EXE 主程序：pywebview 控制面板 + 真实桌面图标物理
import os, sys, threading, time
import webview
import desktop_ctrl
import physics
from mouse_finder import MouseFinder

sim = physics.DesktopSim()
mouse = MouseFinder()
current = None
_lock = threading.Lock()

def physics_loop():
    while True:
        with _lock:
            if sim.running:
                sim.tick()
        time.sleep(1/30.0)

class API:
    def ready(self):
        try:
            n = sim.load()
        except Exception as e:
            return {"ok": False, "error": str(e)}
        return {"ok": True, "count": n, "w": sim.W, "h": sim.H}

    def start(self, name):
        try:
            if name == "mouse":
                mouse.start()
                return {"ok": True, "mouse": True}
            if not sim.orig:
                sim.load()
            sim.start(name)
            return {"ok": True, "count": len(sim.pos), "effect": name}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def stop(self, name=None):
        try:
            if name == "mouse":
                mouse.stop()
                return {"ok": True}
            sim.restore()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def stop_all(self):
        try:
            sim.restore()
            mouse.stop()
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

def on_closed():
    try:
        sim.restore()
        mouse.stop()
    except Exception:
        pass

def resource_path(rel):
    base = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, rel)

if __name__ == "__main__":
    threading.Thread(target=physics_loop, daemon=True).start()
    window = webview.create_window(
        "Young 桌面操控器",
        url=resource_path("ui.html"),
        js_api=API(),
        width=440,
        height=680,
        on_top=True,
    )
    window.events.closed += on_closed
    webview.start(on_top=True)
