/**
 * Editable Snapshot 编辑态工具
 * 
 * 使用方式：在HTML的 </body> 前引入此脚本
 * <script src="../工具链/editable-snapshot.js"></script>
 * 
 * 功能：
 * 1. 自动给 .snapshot 容器添加 contenteditable="true"
 * 2. 右下角浮动「📸 导出4K图片」按钮
 * 3. 点击按钮自动隐藏按钮本身，生成3倍分辨率PNG并下载
 * 
 * 依赖：html2canvas（自动从CDN加载）
 */
(function() {
  // 1. 激活编辑态
  const snapshot = document.querySelector('.snapshot');
  if (snapshot) {
    snapshot.setAttribute('contenteditable', 'true');
  }

  // 2. 加载 html2canvas（多CDN回退）
  const cdns = [
    'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js',
    'https://unpkg.com/html2canvas@1.4.1/dist/html2canvas.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js'
  ];

  function loadScript(url) {
    return new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = url;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  async function loadHtml2Canvas() {
    for (const url of cdns) {
      try {
        await loadScript(url);
        if (typeof html2canvas !== 'undefined') return true;
      } catch(e) { /* try next */ }
    }
    return false;
  }

  loadHtml2Canvas();

  // 3. 创建浮动按钮
  const btn = document.createElement('button');
  btn.id = 'saveBtn';
  btn.textContent = '📸 导出4K图片';
  btn.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;padding:12px 24px;background:linear-gradient(135deg,#2563eb,#1d4ed8);color:#fff;border:none;border-radius:10px;font-size:14px;font-weight:700;cursor:pointer;box-shadow:0 4px 14px rgba(37,99,235,.4);transition:transform .2s';
  btn.onmouseover = function() { this.style.transform = 'scale(1.05)'; };
  btn.onmouseout = function() { this.style.transform = 'scale(1)'; };
  document.body.appendChild(btn);

  // 4. 导出逻辑
  btn.addEventListener('click', async function() {
    const origText = btn.textContent;
    btn.textContent = '⏳ 生成中...';
    btn.style.pointerEvents = 'none';

    try {
      // 等待 html2canvas 加载完成（最多10秒）
      let waited = 0;
      while (typeof html2canvas === 'undefined' && waited < 10000) {
        await new Promise(r => setTimeout(r, 200));
        waited += 200;
      }

      if (typeof html2canvas === 'undefined') {
        throw new Error('html2canvas 加载失败，请检查网络连接');
      }

      // 隐藏按钮再截图
      btn.style.display = 'none';

      const el = document.querySelector('.snapshot');
      const canvas = await html2canvas(el, {
        scale: 3,
        useCORS: true,
        backgroundColor: '#ffffff',
        logging: false
      });

      const link = document.createElement('a');
      const title = document.title || 'snapshot';
      link.download = title.replace(/[^\w\u4e00-\u9fa5]/g, '_') + '_4K.png';
      link.href = canvas.toDataURL('image/png');
      link.click();

      btn.style.display = '';
      btn.textContent = '✅ 已保存';
      setTimeout(() => { btn.textContent = '📸 导出4K图片'; }, 2000);
    } catch(e) {
      btn.style.display = '';
      btn.textContent = '❌ ' + (e.message || '失败，请重试');
      console.error(e);
      setTimeout(() => { btn.textContent = '📸 导出4K图片'; }, 3000);
    }

    btn.style.pointerEvents = '';
  });
})();
