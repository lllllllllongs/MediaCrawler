const PLATFORM_CONFIG = {
  kuaishou: { label: '快手', api: '/api/dashboard/kuaishou' },
  douyin: { label: '抖音', api: '/api/dashboard/douyin' },
  xiaohongshu: { label: '小红书', api: '/api/dashboard/xiaohongshu' }
};

const state = { rows: [] };
const fmt = value => new Intl.NumberFormat('zh-CN').format(Number(value) || 0);
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => (
  {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]
));

function compact(value) {
  const number = Number(value) || 0;
  if (number >= 100000000) return `${(number / 100000000).toFixed(1)}亿`;
  if (number >= 10000) return `${(number / 10000).toFixed(1)}万`;
  return fmt(number);
}

function drawBars(target, rows, field) {
  const max = Math.max(...rows.map(row => Number(row[field]) || 0), 1);
  document.getElementById(target).innerHTML = rows.length ? rows.map(row => `
    <div class="bar-row">
      <div class="bar-label" title="${esc(row.title)}">${esc(row.title || '无标题')}</div>
      <div class="track"><div class="fill" style="width:${(Number(row[field]) || 0) / max * 100}%"></div></div>
      <div>${fmt(row[field])}</div>
    </div>`).join('') : '<div class="empty">暂无数据</div>';
}

function renderTable() {
  const term = document.getElementById('search').value.trim().toLowerCase();
  const relevance = document.getElementById('relevance').value;
  const sort = document.getElementById('sort').value;
  const fields = {
    likes: 'like_count',
    views: 'view_count',
    collected: 'collected_count',
    comments: 'comment_count',
    captured: 'captured_comment_count'
  };
  const rows = state.rows.filter(row => {
    const text = `${row.title} ${row.author} ${row.content_id} ${row.source_keyword}`.toLowerCase();
    const matchesText = !term || text.includes(term);
    const matchesRelevance = relevance === 'all'
      || (relevance === 'relevant' ? row.relevance !== '弱相关' : row.relevance === relevance);
    return matchesText && matchesRelevance;
  }).sort((a, b) => (Number(b[fields[sort]]) || 0) - (Number(a[fields[sort]]) || 0));

  const body = document.getElementById('rows');
  if (!rows.length) {
    body.innerHTML = '<tr><td class="empty" colspan="12">当前筛选条件下暂无数据</td></tr>';
    return;
  }
  body.innerHTML = rows.map(row => {
    const tagClass = row.relevance === '明确漫剧' ? 'exact' : row.relevance === '相关内容' ? 'related' : 'weak';
    return `<tr>
      <td><span class="tag ${tagClass}" title="${esc(row.relevance_reason)}">${esc(row.relevance)}</span></td>
      <td class="title-cell">${esc(row.title)}</td>
      <td>${esc(row.author)}</td>
      <td>${esc(row.publish_time)}</td>
      <td>${fmt(row.view_count)}</td>
      <td>${fmt(row.like_count)}</td>
      <td>${fmt(row.collected_count)}</td>
      <td>${fmt(row.comment_count)}</td>
      <td>${fmt(row.captured_comment_count)}</td>
      <td class="comment-cell">${esc(row.top_comment)}${row.top_comment ? ` (${fmt(row.top_comment_likes)}赞)` : ''}</td>
      <td>${esc(row.source_keyword)}</td>
      <td>${row.url ? `<a class="table-link" href="${esc(row.url)}" target="_blank" rel="noopener">查看</a>` : '-'}</td>
    </tr>`;
  }).join('');
}

function renderDashboard(data) {
  state.rows = data.rows;
  const summary = data.summary;
  document.getElementById('contentCount').textContent = fmt(summary.content_count);
  document.getElementById('relevantCount').textContent = fmt(summary.relevant_count);
  document.getElementById('totalViews').textContent = compact(summary.total_views);
  document.getElementById('totalLikes').textContent = compact(summary.total_likes);
  document.getElementById('totalCollected').textContent = compact(summary.total_collected);

  const relevant = state.rows.filter(row => row.relevance !== '弱相关');
  drawBars('likesChart', [...relevant].sort((a, b) => b.like_count - a.like_count).slice(0, 10), 'like_count');
  drawBars('commentsChart', [...relevant].sort((a, b) => b.comment_count - a.comment_count).slice(0, 10), 'comment_count');
  renderTable();

  const updateTime = data.updated_at
    ? new Date(data.updated_at).toLocaleString('zh-CN')
    : '暂无记录';
  document.getElementById('status').textContent = `数据源：MySQL · 最近更新时间：${updateTime} · 每60秒自动刷新`;
  document.getElementById('status').classList.remove('error');
  document.getElementById('note').textContent =
    `数据库内容 ${summary.content_count} 条，数据库评论 ${summary.captured_comments} 条。播放量为0表示该平台当前数据表未提供播放指标。`;
}

async function loadDashboard() {
  const platform = document.body.dataset.platform;
  const config = PLATFORM_CONFIG[platform];
  try {
    const response = await fetch(config.api, {cache: 'no-store'});
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || `读取失败 (${response.status})`);
    renderDashboard(data);
  } catch (error) {
    const status = document.getElementById('status');
    status.textContent = error.message;
    status.classList.add('error');
  }
}

['search', 'relevance', 'sort'].forEach(id => {
  document.getElementById(id).addEventListener('input', renderTable);
});
loadDashboard();
window.setInterval(loadDashboard, 60000);
