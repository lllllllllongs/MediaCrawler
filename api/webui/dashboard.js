const PLATFORM_CONFIG = {
  kuaishou: { label: '\u5feb\u624b', api: '/api/dashboard/kuaishou' },
  douyin: { label: '\u6296\u97f3', api: '/api/dashboard/douyin' },
  xiaohongshu: { label: '\u5c0f\u7ea2\u4e66', api: '/api/dashboard/xiaohongshu' },
  bilibili: { label: 'B\u7ad9', api: '/api/dashboard/bilibili' },
  weibo: { label: '\u5fae\u535a', api: '/api/dashboard/weibo' },
  tieba: { label: '\u8d34\u5427', api: '/api/dashboard/tieba' },
  zhihu: { label: '\u77e5\u4e4e', api: '/api/dashboard/zhihu' },
  cctv_news: { label: '\u592e\u89c6\u793e\u4f1a\u65b0\u95fb', api: '/api/dashboard/cctv_news' },
  cctv_people: { label: '\u592e\u89c6\u4eba\u7269', api: '/api/dashboard/cctv_people' }
};

const state = { rows: [] };
const collectionMap = {};
const fmt = value => new Intl.NumberFormat('zh-CN').format(Number(value) || 0);
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => (
  {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]
));

function compact(value) {
  const number = Number(value) || 0;
  if (number >= 100000000) return (number / 100000000).toFixed(1) + '\u4ebf';
  if (number >= 10000) return (number / 10000).toFixed(1) + '\u4e07';
  return fmt(number);
}

function drawBars(target, rows, field) {
  const el = document.getElementById(target);
  if (!el) { console.warn('drawBars: element not found', target); return; }
  const max = Math.max(...rows.map(row => Number(row[field]) || 0), 1);
  el.innerHTML = rows.length ? rows.map(row => '\n    <div class="bar-row">\n      <div class="bar-label" title="' + esc(row.title) + '">' + esc(row.title || '\u65e0\u6807\u9898') + '</div>\n      <div class="track"><div class="fill" style="width:' + ((Number(row[field]) || 0) / max * 100) + '%"></div></div>\n      <div>' + fmt(row[field]) + '</div>\n    </div>').join('') : '<div class="empty">\u6682\u65e0\u6570\u636e</div>';
}

async function loadCollectionStatuses() {
  try {
    const resp = await fetch('/api/dashboard/collection', { cache: 'no-store' });
    const data = await resp.json();
    console.log('[collection] loaded', data.count, 'records');
    data.rows.forEach(r => {
      collectionMap[r.platform + ':' + r.content_id] = r;
    });
  } catch(e) { console.warn('[collection] load error:', e); }
}

async function handleCollect(platform, content_id, title, url, author) {
  const tags = prompt('\u8bf7\u8f93\u5165\u6807\u7b7e\uff08\u53ef\u9009\uff0c\u9017\u53f7\u5206\u9694\uff09:');
  if (tags === null) return;
  const notes = prompt('\u8bf7\u8f93\u5165\u5907\u6ce8\uff08\u53ef\u9009\uff09:');
  if (notes === null) return;
  try {
    await fetch('/api/dashboard/collection', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ platform, content_id, title, content_url: url, author, tags, notes })
    });
    collectionMap[platform + ':' + content_id] = { platform, content_id, tags, notes, add_ts: Date.now()/1000 };
    renderTable();
  } catch(e) { alert('\u6536\u5f55\u5931\u8d25: ' + e); }
}

async function handleUncollect(platform, content_id) {
  try {
    await fetch('/api/dashboard/collection', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ platform, content_id })
    });
    delete collectionMap[platform + ':' + content_id];
    renderTable();
  } catch(e) { alert('\u53d6\u6d88\u6536\u5f55\u5931\u8d25: ' + e); }
}

function renderCollectCell(row) {
  const platform = document.body.dataset.platform;
  const key = platform + ':' + row.content_id;
  const collected = !!(collectionMap[key]);
  // Build safe data attributes - use data-json for complex data
  const rowJson = JSON.stringify({ cid: row.content_id, t: row.title, u: row.url, a: row.author });
  if (collected) {
    return '<span class="collected-badge" data-action="uncollect" data-platform="' + esc(platform) + '" data-cid="' + esc(row.content_id) + '" title="\u70b9\u51fb\u53d6\u6d88\u6536\u5f55">\u5df2\u6536\u5f55</span>';
  }
  return '<button class="collect-btn" data-action="collect" data-platform="' + esc(platform) + '" data-cid="' + esc(row.content_id) + '" data-json="' + esc(rowJson) + '">\u6536\u5f55</button>';
}

function renderTable() {
  console.log('[renderTable] start, rows:', state.rows.length);
  const platform = document.body.dataset.platform;
  const config = PLATFORM_CONFIG[platform];
  if (!config) { console.warn('[renderTable] no config for platform:', platform); return; }
  const term = (document.getElementById('search').value || '').trim().toLowerCase();
  const relevanceEl = document.getElementById('relevance');
  const relevance = relevanceEl ? relevanceEl.value : 'all';
  const sortEl = document.getElementById('sort');
  const sort = sortEl ? sortEl.value : 'likes';
  const fields = { likes: 'like_count', views: 'view_count', collected: 'collected_count', comments: 'comment_count', captured: 'captured_comment_count' };
  var rows = state.rows.filter(row => {
    const text = (row.title + ' ' + row.author + ' ' + row.content_id + ' ' + row.source_keyword).toLowerCase();
    return (!term || text.includes(term)) && (relevance === 'all' || (relevance === 'relevant' ? row.relevance !== '\u5f31\u76f8\u5173' : row.relevance === relevance));
  }).sort((a, b) => (Number(b[fields[sort]]) || 0) - (Number(a[fields[sort]]) || 0));
  console.log('[renderTable] filtered rows:', rows.length);

  const body = document.getElementById('rows');
  if (!rows.length) {
    body.innerHTML = '<tr><td class="empty" colspan="14">\u5f53\u524d\u7b5b\u9009\u6761\u4ef6\u4e0b\u6682\u65e0\u6570\u636e</td></tr>';
    return;
  }
  var html = rows.map(row => {
    var h = '<tr>';
    if (row.relevance !== undefined) {
      var tc = row.relevance === '\u660e\u786e\u6f2b\u5267' ? 'exact' : row.relevance === '\u76f8\u5173\u5185\u5bb9' ? 'related' : 'weak';
      h += '<td><span class="tag ' + tc + '" title="' + esc(row.relevance_reason) + '">' + esc(row.relevance) + '</span></td>';
    }
    h += '<td class="title-cell">' + esc(row.title) + '</td>';
    h += '<td>' + esc(row.author) + '</td>';
    h += '<td>' + esc(row.publish_time) + '</td>';
    h += '<td>' + fmt(row.view_count) + '</td>';
    h += '<td>' + fmt(row.like_count) + '</td>';
    h += '<td>' + fmt(row.collected_count) + '</td>';
    h += '<td>' + fmt(row.comment_count) + '</td>';
    var extraCols = ['kuaishou', 'douyin', 'xiaohongshu'];
    if (extraCols.includes(platform)) {
      h += '<td>' + fmt(row.captured_comment_count) + '</td>';
      h += '<td class="comment-cell">' + esc(row.top_comment) + (row.top_comment ? ' (' + fmt(row.top_comment_likes) + '\u8d5e)' : '') + '</td>';
    } else if (platform === 'bilibili') {
      h += '<td>' + fmt(row.share_count) + '</td>';
      h += '<td>' + fmt(row.captured_comment_count) + '</td>';
    } else if (platform === 'weibo' || platform === 'tieba') {
      h += '<td>' + fmt(row.share_count) + '</td>';
    }
    h += '<td>' + esc(row.source_keyword) + '</td>';
    h += '<td class="link-cell">' + (row.url ? '<a class="table-link" href="' + esc(row.url) + '" target="_blank" rel="noopener">查看</a> <button class="copy-link-btn" data-action="copy-link" data-url="' + esc(row.url) + '" title="复制链接">📋</button>' : '-') + '</td>';
    var cell = renderCollectCell(row);
    h += '<td class="collect-cell">' + cell + '</td>';
    h += '</tr>';
    return h;
  }).join('');
  console.log('[renderTable] html length:', html.length, 'has collect-btn:', html.indexOf('collect-btn') >= 0);
  body.innerHTML = html;
}

// Event delegation
document.addEventListener('click', function(e) {
  var btn = e.target.closest('[data-action]');
  if (!btn) return;
  e.preventDefault();
  var action = btn.dataset.action;
  var platform = btn.dataset.platform;
  var cid = btn.dataset.cid;
  console.log('[click] action:', action, 'platform:', platform, 'cid:', cid);
  if (action === 'collect') {
    var jsonStr = btn.dataset.json;
    var rowData = {};
    try { rowData = JSON.parse(jsonStr); } catch(ex) { console.warn('json parse error:', ex); }
    handleCollect(platform, cid, rowData.t || '', rowData.u || '', rowData.a || '');
  } else if (action === 'uncollect') {
    handleUncollect(platform, cid);
  } else if (action === 'copy-link') {
    var url = btn.dataset.url;
    if (url) {
      navigator.clipboard.writeText(url).then(function() {
        var orig = btn.textContent;
        btn.textContent = '✅';
        setTimeout(function() { btn.textContent = orig; }, 1500);
      }).catch(function() {
        alert('复制失败，请手动复制');
      });
    }
  }
});

function renderDashboard(data) {
  console.log('[renderDashboard] rows:', (data.rows || []).length);
  state.rows = data.rows;
  var s = data.summary;
  var el;
  el = document.getElementById('contentCount'); if (el) el.textContent = fmt(s.content_count);
  el = document.getElementById('relevantCount'); if (el) el.textContent = fmt(s.relevant_count);
  el = document.getElementById('totalViews'); if (el) el.textContent = compact(s.total_views);
  el = document.getElementById('totalLikes'); if (el) el.textContent = compact(s.total_likes);
  el = document.getElementById('totalCollected'); if (el) el.textContent = compact(s.total_collected);
  var rel = state.rows.filter(function(r) { return r.relevance !== '\u5f31\u76f8\u5173'; });
  drawBars('likesChart', [].concat(rel).sort(function(a, b) { return b.like_count - a.like_count; }).slice(0, 10), 'like_count');
  drawBars('commentsChart', [].concat(rel).sort(function(a, b) { return b.comment_count - a.comment_count; }).slice(0, 10), 'comment_count');
  renderTable();
  var ut = data.updated_at ? new Date(data.updated_at).toLocaleString('zh-CN') : '\u6682\u65e0\u8bb0\u5f55';
  el = document.getElementById('status');
  if (el) {
    el.textContent = '\u6570\u636e\u6e90\uff1aMySQL \u00b7 \u6700\u8fd1\u66f4\u65b0\u65f6\u95f4\uff1a' + ut + ' \u00b7 \u6bcf60\u79d2\u81ea\u52a8\u5237\u65b0';
    el.classList.remove('error');
  }
  el = document.getElementById('note');
  if (el) el.textContent = '\u6570\u636e\u5e93\u5185\u5bb9 ' + s.content_count + ' \u6761\uff0c\u6570\u636e\u5e93\u8bc4\u8bba ' + (s.captured_comments || 0) + ' \u6761\u3002';
}

async function loadDashboard() {
  console.log('[loadDashboard] start');
  var platform = document.body.dataset.platform;
  var config = PLATFORM_CONFIG[platform];
  if (!config) { console.warn('[loadDashboard] no config for:', platform); return; }
  try {
    await loadCollectionStatuses();
    var response = await fetch(config.api, {cache: 'no-store'});
    var data = await response.json();
    if (!response.ok) throw new Error(data.detail || '\u8bfb\u53d6\u5931\u8d25 (' + response.status + ')');
    renderDashboard(data);
  } catch (error) {
    console.error('[loadDashboard] error:', error);
    var status = document.getElementById('status');
    if (status) {
      status.textContent = error.message;
      status.classList.add('error');
    }
  }
}

['search', 'relevance', 'sort'].forEach(function(id) {
  var el = document.getElementById(id);
  if (el) el.addEventListener('input', renderTable);
});
console.log('[dashboard.js] init, platform:', document.body.dataset.platform);
loadDashboard();
window.setInterval(loadDashboard, 60000);
