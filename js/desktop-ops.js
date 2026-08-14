// ========== 桌面操作合集 - 核心逻辑 ==========

// 模拟桌面图标数据
const DESKTOP_ICONS = [
    { icon: '📁', label: '文档', x: 30, y: 30 },
    { icon: '🖥️', label: '此电脑', x: 30, y: 120 },
    { icon: '🌐', label: '浏览器', x: 30, y: 210 },
    { icon: '📧', label: '邮箱', x: 30, y: 300 },
    { icon: '🎮', label: '游戏', x: 130, y: 30 },
    { icon: '🎵', label: '音乐', x: 130, y: 120 },
    { icon: '📷', label: '照片', x: 130, y: 210 },
    { icon: '⚙️', label: '设置', x: 130, y: 300 },
    { icon: '💼', label: '工作', x: 230, y: 30 },
    { icon: '🗑️', label: '回收站', x: 230, y: 120 },
    { icon: '📝', label: '记事本', x: 230, y: 210 },
    { icon: '🎬', label: '视频', x: 230, y: 300 },
];

let activeEffects = new Set();
let animationFrameId = null;
let iconsState = []; // 保存图标原始状态
let overlayEl = null;
let containerEl = null;

// 初始化桌面覆盖层
function initDesktopOverlay() {
    if (!overlayEl) {
        overlayEl = document.getElementById('overlay');      // 外层（控制显示/隐藏）
        containerEl = document.getElementById('desktop-icons-container');  // 图标容器
    }
}

// 创建模拟桌面图标
function createDesktopIcons() {
    initDesktopOverlay();
    containerEl.innerHTML = '';
    iconsState = [];

    DESKTOP_ICONS.forEach((item, index) => {
        const el = document.createElement('div');
        el.className = 'desktop-icon';
        el.innerHTML = `
            <div class="desktop-icon-icon">${item.icon}</div>
            <div class="desktop-icon-label">${item.label}</div>
        `;
        // 随机初始位置（模拟桌面网格）
        const baseX = 40 + (index % 6) * 90;
        const baseY = 40 + Math.floor(index / 6) * 100;
        el.style.left = `${baseX}px`;
        el.style.top = `${baseY}px`;

        containerEl.appendChild(el);

        iconsState.push({
            el,
            originX: baseX,
            originY: baseY,
            x: baseX,
            y: baseY,
            vx: 0,
            vy: 0,
            width: 72,
            height: 72
        });
    });
}

// 显示桌面覆盖层
function showOverlay() {
    initDesktopOverlay();
    createDesktopIcons();
    overlayEl.classList.remove('hidden');
}

// 隐藏桌面覆盖层并恢复
function hideOverlay() {
    if (overlayEl) {
        overlayEl.classList.add('hidden');
    }
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = null;
    }
}

// 停止所有效果
function stopAllEffects() {
    activeEffects.clear();
    hideOverlay();
    // 重置所有工具卡片
    document.querySelectorAll('.do-tool.run').forEach(card => {
        card.classList.remove('run');
        const startBtn = card.querySelector('.start');
        const stopBtn = card.querySelector('.stop');
        if (startBtn) startBtn.classList.remove('hidden');
        if (stopBtn) stopBtn.classList.add('hidden');
    });
}

// ========== 1. 重力器 ==========
let gravityActive = false;

function startGravity() {
    if (gravityActive) return;
    gravityActive = true;
    activeEffects.add('gravity');
    const card = document.getElementById('dt-gravity');
    if (card) { card.classList.add('run'); card.querySelector('.start').classList.add('hidden'); card.querySelector('.stop').classList.remove('hidden'); }

    showOverlay();

    const gravity = 0.5; // 重力加速度
    const bounce = 0.6; // 弹性系数
    const friction = 0.98; // 摩擦力

    function gravityLoop() {
        if (!gravityActive) return;

        const containerRect = containerEl.getBoundingClientRect();
        const floor = window.innerHeight - 100;
        const rightBound = window.innerWidth - 80;

        iconsState.forEach(icon => {
            // 应用重力
            icon.vy += gravity;

            // 应用速度
            icon.x += icon.vx;
            icon.y += icon.vy;

            // 地面碰撞
            if (icon.y > floor) {
                icon.y = floor;
                icon.vy *= -bounce;
                icon.vx *= friction;
            }

            // 边界碰撞
            if (icon.x < 0) {
                icon.x = 0;
                icon.vx *= -bounce;
            }
            if (icon.x > rightBound) {
                icon.x = rightBound;
                icon.vx *= -bounce;
            }

            // 天花板
            if (icon.y < 0) {
                icon.y = 0;
                icon.vy *= -bounce;
            }

            // 更新位置
            icon.el.style.left = `${icon.x}px`;
            icon.el.style.top = `${icon.y}px`;

            // 轻微随机水平力（模拟不完美掉落）
            if (Math.random() < 0.02) {
                icon.vx += (Math.random() - 0.5) * 2;
            }
        });

        animationFrameId = requestAnimationFrame(gravityLoop);
    }

    // 给每个图标一个随机的初始水平速度
    iconsState.forEach(icon => {
        icon.vx = (Math.random() - 0.5) * 8;
        icon.vy = 0;
    });

    gravityLoop();
}

function stopGravity() {
    gravityActive = false;
    activeEffects.delete('gravity');

    // 如果没有其他效果在运行，隐藏覆盖层
    if (activeEffects.size === 0 && !mouseFinderActive) {
        hideOverlay();
    }
    const card = document.getElementById('dt-gravity');
    if (card) { card.classList.remove('run'); card.querySelector('.start').classList.remove('hidden'); card.querySelector('.stop').classList.add('hidden'); }
}

// ========== 2. 失重器 ==========
let zeroGActive = false;

function startZeroG() {
    if (zeroGActive) return;
    zeroGActive = true;
    activeEffects.add('zeroG');
    const card = document.getElementById('dt-zeroG');
    if (card) { card.classList.add('run'); card.querySelector('.start').classList.add('hidden'); card.querySelector('.stop').classList.remove('hidden'); }

    showOverlay();

    function zeroGLoop() {
        if (!zeroGActive) return;

        const rightBound = window.innerWidth - 80;
        const bottomBound = window.innerHeight - 100;

        iconsState.forEach(icon => {
            // 缓慢飘动
            icon.vx += (Math.random() - 0.5) * 0.3;
            icon.vy += (Math.random() - 0.5) * 0.3;

            // 限制最大速度
            const maxSpeed = 3;
            icon.vx = Math.max(-maxSpeed, Math.min(maxSpeed, icon.vx));
            icon.vy = Math.max(-maxSpeed, Math.min(maxSpeed, icon.vy));

            // 应用速度
            icon.x += icon.vx;
            icon.y += icon.vy;

            // 边缘反弹（柔和）
            if (icon.x < 0 || icon.x > rightBound) {
                icon.vx *= -0.8;
                icon.x = Math.max(0, Math.min(rightBound, icon.x));
            }
            if (icon.y < 0 || icon.y > bottomBound) {
                icon.vy *= -0.8;
                icon.y = Math.max(0, Math.min(bottomBound, icon.y));
            }

            // 轻微旋转效果
            const rotation = Math.sin(Date.now() / 1000 + icon.originX) * 10;
            icon.el.style.transform = `rotate(${rotation}deg)`;

            icon.el.style.left = `${icon.x}px`;
            icon.el.style.top = `${icon.y}px`;
        });

        animationFrameId = requestAnimationFrame(zeroGLoop);
    }

    iconsState.forEach(icon => {
        icon.vx = (Math.random() - 0.5) * 4;
        icon.vy = (Math.random() - 0.5) * 4;
    });

    zeroGLoop();
}

function stopZeroG() {
    zeroGActive = false;
    activeEffects.delete('zeroG');

    // 移除旋转
    iconsState.forEach(icon => {
        icon.el.style.transform = '';
    });

    if (activeEffects.size === 0 && !mouseFinderActive) {
        hideOverlay();
    }
    const card = document.getElementById('dt-zeroG');
    if (card) { card.classList.remove('run'); card.querySelector('.start').classList.remove('hidden'); card.querySelector('.stop').classList.add('hidden'); }
}

// ========== 3. 图标消失器 ==========
let hideIconsActive = false;
let hideInterval = null;

function startHideIcons() {
    if (hideIconsActive) return;
    hideIconsActive = true;
    activeEffects.add('hide');
    const card = document.getElementById('dt-hide');
    if (card) { card.classList.add('run'); card.querySelector('.start').classList.add('hidden'); card.querySelector('.stop').classList.remove('hidden'); }

    showOverlay();

    // 创建一些"窗口"让图标躲到后面去
    createHidingWindows();

    let step = 0;
    const totalSteps = 20;

    hideInterval = setInterval(() => {
        if (!hideIconsActive || step >= totalSteps) {
            clearInterval(hideInterval);
            return;
        }

        iconsState.forEach((icon, i) => {
            // 让图标逐渐移动到"窗口"后面或边缘
            const progress = step / totalSteps;
            const targetX = (i % 3) * (window.innerWidth / 3) + 50 + Math.random() * 100;
            const targetY = Math.floor(i / 3) * 150 + 50 + Math.random() * 50;

            icon.x = icon.originX + (targetX - icon.originX) * progress;
            icon.y = icon.originY + (targetY - icon.originY) * progress;

            // 逐渐缩小透明度
            icon.el.style.opacity = 1 - progress * 0.7;

            icon.el.style.left = `${icon.x}px`;
            icon.el.style.top = `${icon.y}px`;
        });

        step++;
    }, 200);
}

function createHidingWindows() {
    // 在覆盖层上创建几个"悬浮窗口"
    for (let i = 0; i < 4; i++) {
        const win = document.createElement('div');
        win.className = 'hiding-window';
        win.style.cssText = `
            position: absolute;
            left: ${50 + (i % 2) * 300}px;
            top: ${50 + Math.floor(i / 2) * 250}px;
            width: ${200 + Math.random() * 150}px;
            height: ${120 + Math.random() * 80}px;
            background: linear-gradient(135deg, #ffffff, #f1f5f9);
            border-radius: 8px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.15);
            z-index: 5;
            border: 1px solid #e2e8f0;
        `;
        // 窗口标题栏
        const titleBar = document.createElement('div');
        titleBar.style.cssText = `
            height: 28px;
            background: #f1f5f9;
            border-radius: 7px 7px 0 0;
            display: flex;
            align-items: center;
            padding: 0 10px;
            font-size: 11px;
            color: #64748b;
        `;
        titleBar.innerHTML = `<span style="margin-right:auto">📄 窗口${i+1}</span><span>— □ ✕</span>`;
        win.appendChild(titleBar);

        // 窗口内容
        const content = document.createElement('div');
        content.style.cssText = `
            padding: 12px;
            font-size: 11px;
            color: #94a3b8;
        `;
        content.textContent = ['正在处理...', '加载中...', '请稍候...', '计算中...'][i];
        win.appendChild(content);

        containerEl.appendChild(win);
    }
}

function stopHideIcons() {
    hideIconsActive = false;
    activeEffects.delete('hide');

    if (hideInterval) {
        clearInterval(hideInterval);
        hideInterval = null;
    }

    // 恢复图标位置和透明度
    iconsState.forEach(icon => {
        icon.el.style.left = `${icon.originX}px`;
        icon.el.style.top = `${icon.originY}px`;
        icon.el.style.opacity = '';
        icon.el.style.transform = '';
    });

    // 移除隐藏窗口
    document.querySelectorAll('.hiding-window').forEach(w => w.remove());

    if (activeEffects.size === 0 && !mouseFinderActive) {
        hideOverlay();
    }
    const card = document.getElementById('dt-hide');
    if (card) { card.classList.remove('run'); card.querySelector('.start').classList.remove('hidden'); card.querySelector('.stop').classList.add('hidden'); }
}

// ========== 4. 图标打架器 ==========
let fightActive = false;

function startFight() {
    if (fightActive) return;
    fightActive = true;
    activeEffects.add('fight');
    const card = document.getElementById('dt-fight');
    if (card) { card.classList.add('run'); card.querySelector('.start').classList.add('hidden'); card.querySelector('.stop').classList.remove('hidden'); }

    showOverlay();

    // 给每个图标分配一个"目标"来追逐
    iconsState.forEach((icon, i) => {
        const targetIndex = (i + 1) % iconsState.length;
        icon.target = iconsState[targetIndex];
        icon.speed = 2 + Math.random() * 3;
        icon.vx = (Math.random() - 0.5) * 6;
        icon.vy = (Math.random() - 0.5) * 6;
    });

    function fightLoop() {
        if (!fightActive) return;

        const rightBound = window.innerWidth - 80;
        const bottomBound = window.innerHeight - 100;

        iconsState.forEach(icon => {
            if (!icon.target) return;

            // 向目标移动
            const dx = icon.target.x - icon.x;
            const dy = icon.target.y - icon.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist > 5) {
                icon.vx += (dx / dist) * 0.3;
                icon.vy += (dy / dist) * 0.3;
            } else {
                // 碰撞！弹开
                icon.vx = (Math.random() - 0.5) * 10;
                icon.vy = (Math.random() - 0.5) * 10;

                // 显示碰撞特效
                icon.el.style.transform = `scale(1.3) rotate(${(Math.random()-0.5)*30}deg)`;
                setTimeout(() => {
                    icon.el.style.transform = '';
                }, 150);
            }

            // 限速
            const maxSpeed = 6;
            const speed = Math.sqrt(icon.vx * icon.vx + icon.vy * icon.vy);
            if (speed > maxSpeed) {
                icon.vx = (icon.vx / speed) * maxSpeed;
                icon.vy = (icon.vy / speed) * maxSpeed;
            }

            // 摩擦力
            icon.vx *= 0.98;
            icon.vy *= 0.98;

            icon.x += icon.vx;
            icon.y += icon.vy;

            // 边界反弹
            if (icon.x < 0 || icon.x > rightBound) {
                icon.vx *= -1;
                icon.x = Math.max(0, Math.min(rightBound, icon.x));
            }
            if (icon.y < 0 || icon.y > bottomBound) {
                icon.vy *= -1;
                icon.y = Math.max(0, Math.min(bottomBound, icon.y));
            }

            icon.el.style.left = `${icon.x}px`;
            icon.el.style.top = `${icon.y}px`;
        });

        animationFrameId = requestAnimationFrame(fightLoop);
    }

    fightLoop();
}

function stopFight() {
    fightActive = false;
    activeEffects.delete('fight');

    iconsState.forEach(icon => {
        icon.el.style.transform = '';
        icon.target = null;
    });

    if (activeEffects.size === 0 && !mouseFinderActive) {
        hideOverlay();
    }
    const card = document.getElementById('dt-fight');
    if (card) { card.classList.remove('run'); card.querySelector('.start').classList.remove('hidden'); card.querySelector('.stop').classList.add('hidden'); }
}

// ========== 5. 鼠标寻找器 ==========
let mouseFinderActive = false;

function startMouseFinder() {
    if (mouseFinderActive) return;
    mouseFinderActive = true;
    activeEffects.add('mouse');
    const card = document.getElementById('dt-mouse');
    if (card) { card.classList.add('run'); card.querySelector('.start').classList.add('hidden'); card.querySelector('.stop').classList.remove('hidden'); }

    const arrow = document.getElementById('mouse-arrow');
    arrow.classList.remove('hidden');

    document.addEventListener('mousemove', updateMouseArrow);
}

function updateMouseArrow(e) {
    if (!mouseFinderActive) return;

    const arrow = document.getElementById('mouse-arrow');
    // 箭头显示在鼠标附近，稍微偏移一点
    const offsetX = -30 + Math.sin(Date.now() / 200) * 10;
    const offsetY = -35 + Math.cos(Date.now() / 200) * 10;

    arrow.style.left = `${e.clientX + offsetX}px`;
    arrow.style.top = `${e.clientY + offsetY}px`;

    // 箭头指向鼠标（轻微晃动）
    const wobble = Math.sin(Date.now() / 100) * 15;
    arrow.style.transform = `rotate(${180 + wobble}deg)`;
}

function stopMouseFinder() {
    mouseFinderActive = false;
    activeEffects.delete('mouse');

    const arrow = document.getElementById('mouse-arrow');
    arrow.classList.add('hidden');

    document.removeEventListener('mousemove', updateMouseArrow);

    const card = document.getElementById('dt-mouse');
    if (card) { card.classList.remove('run'); card.querySelector('.start').classList.remove('hidden'); card.querySelector('.stop').classList.add('hidden'); }
}

// 工具卡片重置辅助函数（保留兼容）
function resetToolCard(toolId) {
    const card = document.getElementById(toolId);
    if (card) {
        card.classList.remove('active');
        const sb = card.querySelector('.tool-start-btn');
        const tb = card.querySelector('.tool-stop-btn');
        if (sb) sb.classList.remove('hidden');
        if (tb) tb.classList.add('hidden');
    }
}

// ========== 文件结束 ==========
