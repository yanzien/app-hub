// ========== App Hub · 主逻辑 ==========

function navigateTo(section){
  document.querySelectorAll('.sec').forEach(s=>s.classList.remove('active'));
  const t=document.getElementById('section-'+section);
  if(t) t.classList.add('active');
  document.querySelectorAll('.nav-link').forEach(l=>l.classList.remove('active'));
  const a=document.querySelector('.nav-link[data-section="'+section+'"]');
  if(a) a.classList.add('active');
  window.scrollTo({top:0,behavior:'smooth'});
}
document.querySelectorAll('.nav-link').forEach(l=>l.addEventListener('click',()=>navigateTo(l.dataset.section)));

// ---- 弹窗通用 ----
function openModal(id){const m=document.getElementById(id);if(m){m.classList.remove('hidden');document.body.style.overflow='hidden';}}
function closeModal(id){const m=document.getElementById(id);if(m){m.classList.add('hidden');document.body.style.overflow='';}}
function closeDesktopOps2(id){closeModal(id);stopAllEffects();}

// ---- 桌面操作弹窗（浏览器模拟） ----
const DO_TOOLS=[
  {id:'gravity',icon:'🌍',name:'桌面重力器',desc:'模拟重力，图标掉落',start:startGravity,stop:stopGravity},
  {id:'zeroG',icon:'🛸',name:'桌面失重器',desc:'太空失重，图标飘浮',start:startZeroG,stop:stopZeroG},
  {id:'hide',icon:'🙈',name:'图标消失器',desc:'躲到窗口后面',start:startHideIcons,stop:stopHideIcons},
  {id:'fight',icon:'🥊',name:'图标打架器',desc:'互相追逐碰撞',start:startFight,stop:stopFight},
  {id:'mouse',icon:'👆',name:'鼠标寻找器',desc:'箭头指向鼠标',start:startMouseFinder,stop:stopMouseFinder},
];
function openDesktopOps(){
  const grid=document.getElementById('do-grid');
  if(grid && !grid.children.length){
    grid.innerHTML=DO_TOOLS.map(t=>`
      <div class="do-tool" id="dt-${t.id}">
        <div class="ti">${t.icon}</div>
        <div class="tn">${t.name}</div>
        <div class="td">${t.desc}</div>
        <button class="start" onclick="runDotool('${t.id}',true)">▶ 开始</button>
        <button class="stop hidden" onclick="runDotool('${t.id}',false)">↺ 恢复</button>
      </div>`).join('');
  }
  openModal('do-modal');
}
function runDotool(id,start){
  const tool=DO_TOOLS.find(t=>t.id===id);
  const card=document.getElementById('dt-'+id);
  if(start){tool.start();card.classList.add('run');card.querySelector('.start').classList.add('hidden');card.querySelector('.stop').classList.remove('hidden');}
  else{tool.stop();card.classList.remove('run');card.querySelector('.start').classList.remove('hidden');card.querySelector('.stop').classList.add('hidden');}
}

// ---- 网页内嵌 ----
function openWebview(title,url){
  document.getElementById('web-title').textContent=title;
  document.getElementById('web-frame').src=url;
  document.getElementById('web-ext').href=url;
  openModal('web-modal');
}
function closeWeb(){closeModal('web-modal');document.getElementById('web-frame').src='';}

// ---- EXE 下载 ----
function scrollToExe(){document.getElementById('desktop-exe').scrollIntoView({behavior:'smooth'});}
function downloadExe(){
  // 指向构建产物（部署后在 release 或同仓库）
  const url='assets/YoungDesktopController.exe';
  const a=document.createElement('a');a.href=url;a.download='YoungDesktopController.exe';a.click();
  setTimeout(()=>alert('若未开始下载，请手动前往 GitHub Releases 获取最新版。'),500);
}

// ESC 关闭
document.addEventListener('keydown',e=>{
  if(e.key==='Escape'){
    document.querySelectorAll('.modal:not(.hidden)').forEach(m=>{m.classList.add('hidden');document.body.style.overflow='';});
    stopAllEffects();
  }
});
// 点击遮罩关闭
document.querySelectorAll('.modal').forEach(m=>m.addEventListener('click',e=>{
  if(e.target===m){m.classList.add('hidden');document.body.style.overflow='';if(m.id==='do-modal')stopAllEffects();}
}));
