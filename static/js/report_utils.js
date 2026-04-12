// ============================================================
// report_utils.js — 嵌入式报表共用工具函数
// 供各子页面的 JS 调用，需在页面 JS 之前加载
// ============================================================

function fmtVal(val, fmt, colored) {
    if (val === null || val === undefined || val === '') return '--';
    let cls = '';
    let text;
    switch (fmt) {
        case 'money':
            if (typeof val !== 'number') val = parseFloat(val) || 0;
            text = Math.abs(val) >= 10000 ? (val / 10000).toFixed(2) + '万' : val.toFixed(2);
            if (colored) cls = val >= 0 ? 'positive' : 'negative';
            break;
        case 'int':
            text = typeof val === 'number' ? val.toLocaleString() : val;
            break;
        case 'num':
            if (typeof val !== 'number') val = parseFloat(val) || 0;
            text = val.toFixed(2);
            break;
        case 'pct':
            if (typeof val !== 'number') val = parseFloat(val) || 0;
            if (Math.abs(val) <= 1 && Math.abs(val) > 0) val = val * 100;
            text = val.toFixed(2) + '%';
            break;
        default:
            text = String(val);
    }
    return cls ? `<span class="${cls}">${text}</span>` : text;
}

function renderEmbedTable(containerId, data, columns) {
    const wrap = document.getElementById(containerId);
    if (!data || !data.length) {
        wrap.innerHTML = '<div class="status-msg">暂无数据</div>';
        return;
    }
    const hasStickyCol = columns.some(c => c.sticky);
    const idxClass = hasStickyCol ? 'sticky-col' : '';

    let html = '<table class="data-table"><thead><tr>';
    html += `<th class="${idxClass}">#</th>`;
    columns.forEach(c => {
        const cls = [c.fmt ? 'num' : '', c.sticky ? 'sticky-col' : ''].filter(Boolean).join(' ');
        html += `<th class="${cls}">${c.label}</th>`;
    });
    html += '</tr></thead><tbody>';
    data.forEach((row, i) => {
        const isSummary = (row['时段'] === null || row['hours'] === null) && i === data.length - 1;
        html += `<tr class="${isSummary ? 'summary-row' : ''}">`;
        html += `<td class="${idxClass}">${isSummary ? '合计' : i + 1}</td>`;
        columns.forEach(c => {
            const cls = [c.fmt ? 'num' : '', c.sticky ? 'sticky-col' : ''].filter(Boolean).join(' ');
            html += `<td class="${cls}">${fmtVal(row[c.key], c.fmt, c.colored)}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;

    if (hasStickyCol) {
        const headerCells = wrap.querySelectorAll('thead tr .sticky-col');
        const lefts = [];
        let acc = 0;
        headerCells.forEach(cell => { lefts.push(acc); acc += cell.offsetWidth; });
        const lastIdx = lefts.length - 1;
        wrap.querySelectorAll('tr').forEach(tr => {
            tr.querySelectorAll('.sticky-col').forEach((cell, i) => {
                cell.style.left = (lefts[i] ?? 0) + 'px';
                if (i === lastIdx) cell.classList.add('sticky-last');
            });
        });
    }
}

function applyPreset(preset, startId, endId) {
    const today = new Date(); today.setHours(0, 0, 0, 0);
    let s, e;
    switch (preset) {
        case 'today':     s = e = new Date(today); break;
        case 'yesterday': s = e = new Date(today - 86400000); break;
        case '7d':        s = new Date(today - 6 * 86400000); e = new Date(today); break;
        case '30d':       s = new Date(today - 29 * 86400000); e = new Date(today); break;
        case 'thismonth': s = new Date(today.getFullYear(), today.getMonth(), 1); e = new Date(today); break;
        case 'lastmonth': s = new Date(today.getFullYear(), today.getMonth() - 1, 1);
                          e = new Date(today.getFullYear(), today.getMonth(), 0); break;
        default: return;
    }
    const fmt = d => d.toISOString().slice(0, 10);
    document.getElementById('f_' + startId).value = fmt(s);
    document.getElementById('f_' + endId).value   = fmt(e);
    const rangeEl = document.getElementById('range_' + startId);
    if (rangeEl && rangeEl._flatpickr) rangeEl._flatpickr.setDate([s, e]);
}

function initRangePicker(startId, endId) {
    const rangeEl = document.getElementById('range_' + startId);
    if (!rangeEl || typeof flatpickr === 'undefined') return;
    if (rangeEl._flatpickr) rangeEl._flatpickr.destroy();
    flatpickr(rangeEl, {
        mode: 'range', locale: 'zh', dateFormat: 'Y-m-d', disableMobile: true,
        onChange(dates) {
            if (dates.length === 2) {
                document.getElementById('f_' + startId).value = flatpickr.formatDate(dates[0], 'Y-m-d');
                document.getElementById('f_' + endId).value   = flatpickr.formatDate(dates[1], 'Y-m-d');
            }
        }
    });
}
