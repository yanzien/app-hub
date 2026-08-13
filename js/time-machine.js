// ========== 时光机 (Time Machine) - 核心逻辑 ==========

let travelTimer = null;
let travelStartTime = null;
let travelDuration = 0; // 毫秒
let abortAvailable = false;

// 时间单位转毫秒
function timeToMs(value, unit) {
    const multipliers = {
        seconds: 1000,
        minutes: 60 * 1000,
        hours: 60 * 60 * 1000,
        days: 24 * 60 * 60 * 1000
    };
    return value * (multipliers[unit] || 1000);
}

// 格式化时间显示
function formatTimeDuration(ms) {
    if (ms < 1000) return `${ms}毫秒`;
    if (ms < 60000) return `${Math.round(ms / 1000)}秒`;
    if (ms < 3600000) return `${Math.round(ms / 60000)}分钟`;
    if (ms < 86400000) return `${Math.round(ms / 3600000)}小时`;
    return `${Math.round(ms / 86400000)}天`;
}

// 切换面板
function showTMPanel(panelId) {
    document.querySelectorAll('.tm-panel').forEach(p => p.classList.remove('active'));
    const panel = document.getElementById(panelId);
    if (panel) panel.classList.add('active');
}

// 重置时光机到主界面
function resetTimeMachine() {
    if (travelTimer) {
        clearInterval(travelTimer);
        travelTimer = null;
    }
    showTMPanel('tm-main');
    document.getElementById('custom-time-panel').classList.add('hidden');
    document.getElementById('abort-btn-container').classList.add('hidden');
    abortAvailable = false;

    // 重置进度条
    const progressFill = document.getElementById('travel-progress');
    const percentText = document.getElementById('travel-percent');
    if (progressFill) progressFill.style.width = '0%';
    if (percentText) percentText.textContent = '0%';
}

// 开始穿越（从按钮触发）
document.querySelectorAll('.time-btn[data-time]').forEach(btn => {
    btn.addEventListener('click', () => {
        const value = parseInt(btn.dataset.time);
        const unit = btn.dataset.unit;
        startTravel(value, unit);
    });
});

// 显示自定义时间面板
function showCustomTime() {
    const panel = document.getElementById('custom-time-panel');
    panel.classList.toggle('hidden');
}

// 自定义穿越
function startCustomTravel() {
    const value = parseInt(document.getElementById('custom-time-value').value);
    const unit = document.getElementById('custom-time-unit').value;
    if (!value || value < 1) {
        alert('请输入有效的时间数值！');
        return;
    }
    startTravel(value, unit);
}

// ===== 核心穿越逻辑 =====
function startTravel(value, unit) {
    travelDuration = timeToMs(value, unit);
    travelStartTime = Date.now();

    // 判断是否显示中途退出按钮（超过30秒才显示）
    abortAvailable = travelDuration >= 30000;

    showTMPanel('tm-traveling');
    document.getElementById('tm-traveling').classList.add('active');

    if (abortAvailable) {
        document.getElementById('abort-btn-container').classList.remove('hidden');
    } else {
        document.getElementById('abort-btn-container').classList.add('hidden');
    }

    // 重置进度条
    const progressFill = document.getElementById('travel-progress');
    const percentText = document.getElementById('travel-percent');
    progressFill.style.width = '0%';
    percentText.textContent = '0%';

    // 启动进度更新
    travelTimer = setInterval(() => {
        const elapsed = Date.now() - travelStartTime;
        let progress = Math.min((elapsed / travelDuration) * 100, 100);

        progressFill.style.width = `${progress}%`;
        percentText.textContent = `${Math.round(progress)}%`;

        if (progress >= 100) {
            clearInterval(travelTimer);
            travelTimer = null;
            onTravelComplete(value, unit);
        }
    }, 50); // 每50ms更新一次，让动画更流畅
}

// 穿越完成
function onTravelComplete(value, unit) {
    const durationStr = formatTimeDuration(travelDuration);

    let message, detail;
    if (unit === 'seconds' && value <= 5) {
        message = `恭喜你穿越到 ${value} 秒后了！`;
        detail = `你成功穿越了 ${value} 秒，现在的时间是 ${new Date().toLocaleTimeString()}`;
    } else if (unit === 'minutes' && value === 1) {
        message = '恭喜你穿越到 1 分钟后了！';
        detail = `你成功穿越了 1 分钟，现在的时间是 ${new Date().toLocaleTimeString()}。感觉如何？是不是感觉自己变年轻了？`;
    } else if (unit === 'minutes' && value === 5) {
        message = '恭喜你穿越到 5 分钟后了！';
        detail = `5分钟的漫长等待，你居然坚持下来了！现在的时间是 ${new Date().toLocaleTimeString()}`;
    } else if (unit === 'hours') {
        message = `恭喜你穿越到 ${value} 小时后了！`;
        detail = `你真的等了 ${value} 个小时！这毅力，佩服！现在的时间是 ${new Date().toLocaleTimeString()}`;
    } else if (unit === 'days') {
        message = `恭喜你穿越到 ${value} 天后了！`;
        detail = `${value}天后... 你还在？现在的时间是 ${new Date().toLocaleDateString()}`;
    } else {
        message = `恭喜你穿越到 ${durationStr} 后了！`;
        detail = `穿越耗时：${durationStr}。当前时间：${new Date().toLocaleString()}`;
    }

    document.getElementById('success-message').textContent = message;
    document.getElementById('success-detail').textContent = detail;
    showTMPanel('tm-success');
}

// 中途退出
function abortTravel() {
    showTMPanel('tm-abort-confirm');
}

function confirmAbort() {
    const elapsed = Date.now() - travelStartTime;
    const elapsedStr = formatTimeDuration(elapsed);

    clearInterval(travelTimer);
    travelTimer = null;

    document.getElementById('success-message').textContent = `你中途退出了！`;
    document.getElementById('success-detail').textContent =
        `你只穿越了 ${elapsedStr}。虽然没完成全程，但至少你尝试过！\n` +
        `(警告中提到的后果均未发生，大概吧...)`;

    // 更新成功界面文字
    const factEl = document.querySelector('.success-fact p');
    if (factEl) {
        factEl.textContent = '💡 好消息：时空裂缝已自动修复，平行宇宙未分裂，你仍然只有一个你。';
    }

    showTMPanel('tm-success');
}

function cancelAbort() {
    showTMPanel('tm-traveling');
}

// ===== 穿越到过去功能 =====
function showPastTravel() {
    showTMPanel('tm-past');
}

function backToTMMain() {
    showTMPanel('tm-main');
}

function backToTMPast() {
    showTMPanel('tm-past');
}

// 支付弹窗
function showPayment() {
    showTMPanel('tm-payment');
}
