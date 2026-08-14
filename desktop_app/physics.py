# physics.py
# 在真实桌面图标坐标上运行物理模拟，并把结果写回桌面
import math
import random
import desktop_ctrl

ICON_W = 80
ICON_H = 80

class DesktopSim:
    def __init__(self):
        self.effect = None
        self.orig = []        # [(x,y)]
        self.pos = []         # [(x,y)]
        self.vel = []         # [(vx,vy)]
        self.target = []      # [(tx,ty)] 用于消失器目标
        self._last_written = []  # 上次写回的位置，避免重复刷新
        self.running = False
        self.W, self.H = desktop_ctrl.screen_size()

    def load(self):
        self.orig = desktop_ctrl.get_positions()
        self.pos = [list(p) for p in self.orig]
        self.vel = [[0.0, 0.0] for _ in self.orig]
        self.target = [list(p) for p in self.orig]
        self.W, self.H = desktop_ctrl.screen_size()
        return len(self.orig)

    def start(self, effect):
        if not self.orig:
            self.load()
        self.effect = effect
        self.running = True
        self._last_written = []  # 重置，确保首次 tick 一定写入
        n = len(self.pos)
        if effect == "gravity":
            self.vel = [[(random.random()-0.5)*4, 0.0] for _ in range(n)]
        elif effect == "zeroG":
            self.vel = [[(random.random()-0.5)*5, (random.random()-0.5)*5] for _ in range(n)]
        elif effect == "fight":
            self.vel = [[(random.random()-0.5)*8, (random.random()-0.5)*8] for _ in range(n)]
            self._assign_targets()
        elif effect == "hide":
            # 把目标设为屏幕外/边缘，逐渐移走
            self.target = []
            for i in range(n):
                side = i % 4
                if side == 0:
                    self.target.append([-ICON_W, random.randint(0, self.H)])
                elif side == 1:
                    self.target.append([self.W, random.randint(0, self.H)])
                elif side == 2:
                    self.target.append([random.randint(0, self.W), -ICON_H])
                else:
                    self.target.append([random.randint(0, self.W), self.H+ICON_H])

    def _assign_targets(self):
        n = len(self.pos)
        self._tgt_idx = [(i+1) % n for i in range(n)]

    def stop(self):
        self.running = False
        self.effect = None

    def restore(self):
        self.running = False
        self.effect = None
        if self.orig:
            desktop_ctrl.set_positions([tuple(p) for p in self.orig])

    def tick(self):
        if not self.running or not self.pos:
            return
        n = len(self.pos)
        floor = self.H - ICON_H
        right = self.W - ICON_W
        if self.effect == "gravity":
            g = 0.6
            for i in range(n):
                self.vel[i][1] += g
                self.pos[i][0] += self.vel[i][0]
                self.pos[i][1] += self.vel[i][1]
                if self.pos[i][1] > floor:
                    self.pos[i][1] = floor
                    self.vel[i][1] *= -0.55
                    self.vel[i][0] *= 0.96
                if self.pos[i][0] < 0:
                    self.pos[i][0] = 0; self.vel[i][0] *= -0.5
                if self.pos[i][0] > right:
                    self.pos[i][0] = right; self.vel[i][0] *= -0.5
                if self.pos[i][1] < 0:
                    self.pos[i][1] = 0; self.vel[i][1] *= -0.5
        elif self.effect == "zeroG":
            for i in range(n):
                self.vel[i][0] += (random.random()-0.5)*0.25
                self.vel[i][1] += (random.random()-0.5)*0.25
                sp = math.hypot(*self.vel[i])
                if sp > 3:
                    self.vel[i][0] *= 3/sp; self.vel[i][1] *= 3/sp
                self.pos[i][0] += self.vel[i][0]
                self.pos[i][1] += self.vel[i][1]
                if self.pos[i][0] < 0 or self.pos[i][0] > right:
                    self.vel[i][0] *= -0.85
                    self.pos[i][0] = max(0, min(right, self.pos[i][0]))
                if self.pos[i][1] < 0 or self.pos[i][1] > floor:
                    self.vel[i][1] *= -0.85
                    self.pos[i][1] = max(0, min(floor, self.pos[i][1]))
        elif self.effect == "fight":
            for i in range(n):
                t = self.pos[self._tgt_idx[i]]
                dx = t[0]-self.pos[i][0]; dy = t[1]-self.pos[i][1]
                d = math.hypot(dx, dy) or 1
                if d > 6:
                    self.vel[i][0] += dx/d*0.35
                    self.vel[i][1] += dy/d*0.35
                else:
                    self.vel[i][0] = (random.random()-0.5)*14
                    self.vel[i][1] = (random.random()-0.5)*14
                sp = math.hypot(*self.vel[i])
                if sp > 7:
                    self.vel[i][0] *= 7/sp; self.vel[i][1] *= 7/sp
                self.vel[i][0] *= 0.99; self.vel[i][1] *= 0.99
                self.pos[i][0] += self.vel[i][0]
                self.pos[i][1] += self.vel[i][1]
                if self.pos[i][0] < 0 or self.pos[i][0] > right:
                    self.vel[i][0] *= -1
                    self.pos[i][0] = max(0, min(right, self.pos[i][0]))
                if self.pos[i][1] < 0 or self.pos[i][1] > floor:
                    self.vel[i][1] *= -1
                    self.pos[i][1] = max(0, min(floor, self.pos[i][1]))
        elif self.effect == "hide":
            for i in range(n):
                dx = self.target[i][0]-self.pos[i][0]
                dy = self.target[i][1]-self.pos[i][1]
                d = math.hypot(dx, dy)
                step = min(d, 12)
                if d > 0.5:
                    self.pos[i][0] += dx/d*step
                    self.pos[i][1] += dy/d*step
        # 只在位置真正变化时才写回桌面（避免闪烁）
        new_pos = [(int(p[0]), int(p[1])) for p in self.pos]
        if new_pos != self._last_written:
            desktop_ctrl.set_positions(new_pos)
            self._last_written = new_pos
