// ========== 网页同步区 · GitHub Pages 集成 ==========

const GITHUB_REPOS = [
  { name:'home', full:'yanzien/home', desc:'🏠 个人主页 · Young 的个人主页，展示基本信息、项目链接与社交账号。简洁现代、响应式、支持深色模式。', url:'https://yanzien.github.io/home', icon:'🏠', featured:true, tags:['个人主页','响应式','Pages'], tech:'HTML/CSS/JS', status:'已部署', upd:'持续更新' },
  { name:'hw', full:'yanzien/hw', desc:'📝 作业助手 · 在线作业管理与提交系统。多科目分类、截止提醒、状态跟踪，帮学生管好学习任务。', url:'https://yanzien.github.io/hw', icon:'📝', featured:true, tags:['作业管理','学生工具','效率'], tech:'Web App', status:'已部署', upd:'活跃开发' },
  { name:'gesp-helper', full:'yanzien/gesp-helper', desc:'💻 GESP C++ 辅助 · 专为 GESP（青少年编程能力等级考试）C++ 学习者设计。题库练习、知识点梳理、模拟测试、错题本，助力考级！', url:'https://yanzien.github.io/gesp-helper', icon:'💻', featured:true, tags:['GESP','C++','编程考试','题库'], tech:'C++ / Web', status:'已部署', upd:'持续更新' },
  { name:'oiwb', full:'yanzien/oiwb', desc:'🧮 OI 题板 · 竞赛编程刷题记录与整理工具。题目收藏、标签分类、解题笔记、难度标记，OIer / ACMer 必备伴侣！', url:'https://yanzien.github.io/oiwb', icon:'🧮', featured:true, tags:['OI','ACM','竞赛','刷题'], tech:'Web App', status:'已部署', upd:'活跃维护' },
  { name:'361-webscanner', full:'yanzien/361-webscanner', desc:'🔍 361 网页扫描器 · 基于 Web 的扫描工具，提供网页内容分析与信息提取。', url:'https://yanzien.github.io/361-webscanner', icon:'🔍', featured:false, tags:['扫描','Web工具'], tech:'Web Tool', status:'已部署', upd:'稳定版' },
  { name:'oitablemaker', full:'yanzien/oitablemaker', desc:'📊 OI 表格制作器 · 为信息学竞赛选手设计的表格生成工具，快速制作比赛记录表、统计表。', url:'https://yanzien.github.io/oitablemaker', icon:'📊', featured:false, tags:['OI','表格','工具'], tech:'Web Tool', status:'已部署', upd:'稳定版' },
  { name:'smartwenshi', full:'yanzien/smartwenshi', desc:'📖 智能文言文 · AI 驱动的文言文学习工具，提供古文解析、注释对照、语法分析。', url:'https://yanzien.github.io/smartwenshi', icon:'📖', featured:false, tags:['文言文','AI','教育'], tech:'AI + Web', status:'已部署', upd:'实验性' },
  { name:'mdqpaste', full:'yanzien/mdqpaste', desc:'📋 MDQ Paste · Markdown 代码粘贴分享工具，语法高亮、一键复制、短链生成。', url:'https://yanzien.github.io/mdqpaste', icon:'📋', featured:false, tags:['Markdown','代码分享'], tech:'Web Tool', status:'已部署', upd:'稳定版' },
  { name:'in-wlxy', full:'yanzien/in-wlxy', desc:'🎓 未来学校入口 · 相关项目入口页面 / 门户应用。', url:'https://yanzien.github.io/in-wlxy', icon:'🎓', featured:false, tags:['校园','门户'], tech:'Web Portal', status:'已部署', upd:'按需更新' },
];

function renderRepoCards(){
  const grid=document.getElementById('repo-grid');
  if(!grid)return;
  grid.innerHTML=GITHUB_REPOS.map(r=>`
    <div class="rcard ${r.featured?'featured':''}" onclick="openWebview('${r.name}','${r.url}')">
      <div class="rc-top">
        <div class="rc-ico">${r.icon}</div>
        <span class="rc-name">${r.full}</span>
        <span class="rc-badge">${r.featured?'⭐ 推荐':'可用'}</span>
      </div>
      <div class="rc-desc">${r.desc}</div>
      <div class="rc-meta">
        <span>🔧 ${r.tech}</span><span>✅ ${r.status}</span><span>🕐 ${r.upd}</span>
      </div>
      <div class="rc-tags">${r.tags.map(t=>`<span>${t}</span>`).join('')}</div>
      <button class="rc-open" onclick="event.stopPropagation();window.open('${r.url}','_blank')">🌐 打开网页</button>
    </div>`).join('');
}
document.addEventListener('DOMContentLoaded',renderRepoCards);
