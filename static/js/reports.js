// ============================================================
// Config: report definitions
// ============================================================
const REPORTS = {
    // === 销售分析 ===
    t1: {
        group: 'sales', label: 'T1 销售客单按时段', api: '/api/t1_sale_bytime',
        filters: ['store','start','end'],
        columns: [
            {key:'c_store_name',label:'门店'},{key:'c_ccode_name',label:'品类'},
            {key:'hours',label:'时段'},{key:'kl',label:'客流',fmt:'int'},
            {key:'kd',label:'客单',fmt:'money'},{key:'sale',label:'销售额',fmt:'money'},
            {key:'salesum',label:'累计销售',fmt:'money'}
        ],
        chart: 'hourly_sale'
    },
    t2: {
        group: 'sales', label: 'T2 总客流日报', api: '/api/daily_flow',
        filters: ['store','start','end'],
        columns: [
            {key:'date',label:'日期'},{key:'weekday',label:'星期'},{key:'store_name',label:'机构'},
            {key:'flow_count',label:'客流',fmt:'int'},{key:'avg_ticket',label:'客单',fmt:'money'},
            {key:'sales',label:'销售额',fmt:'money'},{key:'profit',label:'毛利额',fmt:'money'},
            {key:'profit_rate',label:'毛利率',fmt:'pct'}
        ],
        dataKey: 'rows'
    },
    t4: {
        group: 'sales', label: 'T4 销售时段对比', api: '/api/t4_sale_compare',
        filters: ['store','start','end','cmp_start','cmp_end'],
        columns: [
            {key:'时段',label:'时段'},{key:'销售额',label:'销售额',fmt:'money'},{key:'客流',label:'客流',fmt:'int'},
            {key:'客单',label:'客单',fmt:'money'},{key:'对比销售额',label:'对比销售额',fmt:'money'},
            {key:'对比客流',label:'对比客流',fmt:'int'},{key:'对比客单',label:'对比客单',fmt:'money'},
            {key:'销售差',label:'销售差',fmt:'money',colored:true},{key:'销售对比率',label:'销售对比率',fmt:'pct'},
            {key:'客流差',label:'客流差',fmt:'int',colored:true},{key:'客单差',label:'客单差',fmt:'money',colored:true}
        ],
        chart: 'compare'
    },
    // === 品类分析 ===
    t3: {
        group: 'category', label: 'T3 品类销售分析', api: '/api/t3_category_analysis',
        filters: ['store','start','end','ccode'],
        columns: [
            {key:'品类号码',label:'品类号码'},{key:'品类名称',label:'品类名称'},
            {key:'销售额',label:'销售额',fmt:'money'},{key:'毛利额',label:'毛利额',fmt:'money'},
            {key:'毛利率',label:'毛利率',fmt:'pct'},{key:'来客数',label:'来客数',fmt:'int'},
            {key:'客单价',label:'客单价',fmt:'money'},{key:'品项数',label:'品项数',fmt:'int'},
            {key:'动销数',label:'动销数',fmt:'int'},{key:'动销率',label:'动销率',fmt:'pct'},
            {key:'不动销数',label:'不动销数',fmt:'int'},
            {key:'销售额占比_课占部',label:'课占部(销)',fmt:'pct'},
            {key:'销售额占比_课占店',label:'课占店(销)',fmt:'pct'},
            {key:'毛利额占比_课占部',label:'课占部(利)',fmt:'pct'},
            {key:'毛利额占比_课占店',label:'课占店(利)',fmt:'pct'}
        ]
    },
    t11_2: {
        group: 'category', label: 'T11.2 品类动销率', api: '/api/t11_2_category_movement',
        filters: ['store','start','end','ccode'],
        columns: [
            {key:'分类号码',label:'分类号码'},{key:'分类名称',label:'分类名称'},
            {key:'单品数',label:'单品数',fmt:'int'},{key:'动销数',label:'动销数',fmt:'int'},
            {key:'动销率',label:'动销率',fmt:'pct'},{key:'不动销数',label:'不动销数',fmt:'int'}
        ],
        chart: 'category_movement'
    },
    // === 商品监控 ===
    t5: {
        group: 'product', label: 'T5 畅销缺货', api: '/api/t5_stockout',
        filters: ['store','ccode','warn_days'],
        columns: [
            {key:'商品编码',label:'商品编码'},{key:'商品名称',label:'商品名称'},{key:'商品条码',label:'条码'},
            {key:'规格',label:'规格'},{key:'商品状态',label:'状态'},{key:'销售频率',label:'频率'},
            {key:'进价',label:'进价',fmt:'money'},{key:'售价',label:'售价',fmt:'money'},
            {key:'毛利率',label:'毛利率',fmt:'pct'},{key:'库存',label:'库存',fmt:'num'},
            {key:'日均销售',label:'日均销售',fmt:'num'},{key:'在途',label:'在途',fmt:'int'},
            {key:'品类名称',label:'品类'},{key:'供应商名称',label:'供应商'}
        ]
    },
    t6: {
        group: 'product', label: 'T6 商品销售分析', api: '/api/t6_product_sales',
        filters: ['store','start','end','dept','ccode'],
        columns: [
            {key:'商品编码',label:'商品编码'},{key:'商品名称',label:'商品名称'},{key:'规格',label:'规格'},
            {key:'销售数量',label:'销量',fmt:'num'},{key:'销售额',label:'销售额',fmt:'money'},
            {key:'毛利',label:'毛利',fmt:'money',colored:true},{key:'毛利率',label:'毛利率',fmt:'pct'},
            {key:'品类名称',label:'品类'},{key:'供应商名',label:'供应商'},{key:'当前库存',label:'库存',fmt:'num'}
        ]
    },
    t8: {
        group: 'product', label: 'T8 负毛利', api: '/api/t8_negative_margin',
        filters: ['store','start','end','dept','ccode'],
        columns: [
            {key:'机构名称',label:'机构'},{key:'商品名称',label:'商品'},{key:'商品编码',label:'编码'},
            {key:'条码',label:'条码'},{key:'销售日期',label:'日期'},{key:'销售数量',label:'销量',fmt:'num'},
            {key:'销售金额',label:'销售额',fmt:'money'},{key:'毛利额',label:'毛利额',fmt:'money',colored:true},
            {key:'毛利率',label:'毛利率',fmt:'pct'},{key:'进价',label:'进价',fmt:'money'},
            {key:'售价',label:'售价',fmt:'money'},{key:'库存',label:'库存',fmt:'num'},
            {key:'分类',label:'分类'},{key:'供应商',label:'供应商'}
        ]
    },
    t9: {
        group: 'product', label: 'T9 高库存低周转', api: '/api/t9_high_inventory',
        filters: ['store','ccode','formula'],
        columns: [
            {key:'品类',label:'品类'},{key:'品名',label:'品名'},{key:'规格',label:'规格'},
            {key:'商品品态',label:'品态'},{key:'畅销',label:'畅销'},{key:'进价',label:'进价',fmt:'money'},
            {key:'售价',label:'售价',fmt:'money'},{key:'毛利率',label:'毛利率',fmt:'pct'},
            {key:'库存数量',label:'库存',fmt:'num'},{key:'库存成本',label:'库存成本',fmt:'money'},
            {key:'日均销量',label:'日均销量',fmt:'num'},{key:'计算值',label:'周转天数',fmt:'num'},
            {key:'分类名称',label:'分类'},{key:'主供应商名称',label:'供应商'}
        ]
    },
    t10: {
        group: 'product', label: 'T10 新品报表', api: '/api/t10_new_products',
        filters: ['store','start','end'],
        columns: [
            {key:'商品编码',label:'编码'},{key:'商品名',label:'商品名'},{key:'规格',label:'规格'},
            {key:'新品日',label:'新品日'},{key:'首次进货日期',label:'首进日'},
            {key:'新品天数',label:'新品天数',fmt:'int'},{key:'商品品态',label:'品态'},
            {key:'销售数量',label:'销量',fmt:'num'},{key:'销售金额',label:'销售额',fmt:'money'},
            {key:'销售毛利',label:'毛利',fmt:'money'},{key:'销售毛利率',label:'毛利率',fmt:'pct'},
            {key:'库存数量',label:'库存',fmt:'num'},{key:'日均销售',label:'日均',fmt:'num'},
            {key:'分类名称',label:'分类'}
        ]
    },
    t12: {
        group: 'product', label: 'T12 品态异常', api: '/api/t12_abnormal_status',
        filters: ['store'],
        columns: [
            {key:'品名',label:'品名'},{key:'条码',label:'条码'},{key:'规格',label:'规格'},
            {key:'库存状态',label:'库存状态'},{key:'库存数量',label:'库存',fmt:'num'},
            {key:'日均销量',label:'日均销量',fmt:'num'},
            {key:'最后收货日期',label:'最后收货'},{key:'最后销售日期',label:'最后销售'},
            {key:'分类名称',label:'分类'},{key:'主供应商名称',label:'供应商'}
        ]
    },
    t13: {
        group: 'product', label: 'T13 滞销商品', api: '/api/t13_slow_moving',
        filters: ['store','start','end','dept','ccode','clevel','calc'],
        columns: [
            {key:'机构名称',label:'机构'},{key:'商品编码',label:'编码'},{key:'商品名称',label:'商品'},
            {key:'条码',label:'条码'},{key:'商品品态',label:'品态'},{key:'进价',label:'进价',fmt:'money'},
            {key:'售价',label:'售价',fmt:'money'},{key:'毛利率',label:'毛利率',fmt:'pct'},
            {key:'库存数量',label:'库存',fmt:'num'},{key:'库存成本',label:'库存成本',fmt:'money'},
            {key:'日均销量',label:'日均',fmt:'num'},
            {key:'分类名称',label:'分类'},{key:'主供应商名称',label:'供应商'},
            {key:'销售数量',label:'销量',fmt:'num'},{key:'销售金额',label:'销售额',fmt:'money'},
            {key:'销量排名率',label:'销量排名率',fmt:'pct'},{key:'销额排名率',label:'销额排名率',fmt:'pct'}
        ]
    },
    // === 供应商分析 ===
    t7: {
        group: 'supplier', label: 'T7 供应商到货率', api: '/api/t7_supplier_delivery',
        filters: ['store','start','end','supplier'],
        columns: [
            {key:'供应商号',label:'供应商号',sticky:true},{key:'供应商名称',label:'供应商名称',sticky:true},
            {key:'销售额',label:'销售额',fmt:'money'},{key:'毛利',label:'毛利',fmt:'money'},
            {key:'毛利率',label:'毛利率',fmt:'pct'},{key:'品项数',label:'品项数',fmt:'int'},
            {key:'动销数',label:'动销数',fmt:'int'},{key:'动销率',label:'动销率',fmt:'pct'},
            {key:'订货量',label:'订货量',fmt:'num'},{key:'订货额',label:'订货额',fmt:'money'},
            {key:'到货量',label:'到货量',fmt:'num'},{key:'到货额',label:'到货额',fmt:'money'},
            {key:'到货量率',label:'到货量率',fmt:'pct'},{key:'到货额率',label:'到货额率',fmt:'pct'}
        ]
    },
    t11: {
        group: 'supplier', label: 'T11.1 供应商动销率', api: '/api/t11_supplier_movement',
        filters: ['store','start','end','supplier','ccode'],
        columns: [
            {key:'机构',label:'机构'},{key:'机构名称',label:'机构名称'},
            {key:'供应商号',label:'供应商号'},{key:'供应商名称',label:'供应商名称'},
            {key:'单品数',label:'单品数',fmt:'int'},{key:'动销数',label:'动销数',fmt:'int'},
            {key:'不动销数',label:'不动销数',fmt:'int'},{key:'动销率',label:'动销率',fmt:'pct'}
        ]
    }
};

const GROUPS = {
    sales:    { label: '销售分析',   reports: ['t1','t2','t4'] },
    category: { label: '品类分析',   reports: ['t3','t11_2'] },
    product:  { label: '商品监控',   reports: ['t5','t6','t8','t9','t10','t12','t13'] },
    supplier: { label: '供应商分析', reports: ['t7','t11'] }
};

const T1_AUTO_STORE  = '倾城';
const T1_TEST_DATES  = { start: '2024-09-08', end: '2024-09-09' };

const FILTER_DEFS = {
    store:     { label: '机构',     type: 'select', default: '11021' },
    start:     { label: '开始日期', type: 'date',   default: '' },
    end:       { label: '结束日期', type: 'date',   default: '' },
    cmp_start: { label: '对比开始', type: 'date',   default: '' },
    cmp_end:   { label: '对比结束', type: 'date',   default: '' },
    dept:      { label: '部门',     type: 'text',   default: '', placeholder: '如11' },
    ccode:     { label: '品类编码', type: 'text',   default: '', placeholder: '如22' },
    supplier:  { label: '供应商',   type: 'text',   default: '', placeholder: '编码' },
    warn_days: { label: '预警天数', type: 'number', default: '7' },
    formula:   { label: '计算公式', type: 'select', options: ['基于周转天数','基于安全天数'], default: '基于周转天数' },
    clevel:    { label: '品类层级', type: 'select', options: ['第一层','第二层','第三层'], default: '第三层' },
    calc:      { label: '计算方式', type: 'select', options: ['以上全部','销量6%','销额1%'], default: '以上全部' }
};

// State
let currentGroup  = 'sales';
let currentReport = 't1';
let storeList     = [];
let lastData      = [];
const reportStates = {};

// ============================================================
// Formatting helpers
// ============================================================
function fmtVal(val, fmt, colored) {
    if (val === null || val === undefined || val === '') return '--';
    let cls = '';
    if (colored && typeof val === 'number') {
        cls = val > 0 ? 'positive' : val < 0 ? 'negative' : '';
    }
    let text;
    switch(fmt) {
        case 'money':
            if (typeof val !== 'number') val = parseFloat(val) || 0;
            text = Math.abs(val) >= 10000 ? (val/10000).toFixed(2)+'万' : val.toFixed(2);
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

// ============================================================
// UI Rendering
// ============================================================
function renderSubTabs() {
    const bar     = document.getElementById('subTabBar');
    const reports = GROUPS[currentGroup].reports;
    bar.innerHTML = reports.map(id =>
        `<div class="sub-tab ${id===currentReport?'active':''}" data-report="${id}">${REPORTS[id].label}</div>`
    ).join('');
    bar.querySelectorAll('.sub-tab').forEach(el => {
        el.addEventListener('click', () => {
            currentReport = el.dataset.report;
            renderSubTabs();
            renderFilters();
            if (!restoreState(currentReport)) clearContent();
        });
    });
}

function renderFilters() {
    const bar    = document.getElementById('filterBar');
    const report = REPORTS[currentReport];
    if (!report) return;

    const filters = report.filters;
    const handled = new Set();
    let html = '';

    filters.forEach(fid => {
        if (handled.has(fid)) return;

        if (fid === 'start' && filters.includes('end')) {
            handled.add('start'); handled.add('end');
            html += renderDateRangeGroup('start', 'end', '查询区间');
            return;
        }
        if (fid === 'cmp_start' && filters.includes('cmp_end')) {
            handled.add('cmp_start'); handled.add('cmp_end');
            html += renderDateRangeGroup('cmp_start', 'cmp_end', '对比区间');
            return;
        }

        const def = FILTER_DEFS[fid];
        html += `<div><label>${def.label}</label><br>`;
        if (def.type === 'select' && fid === 'store') {
            html += `<select id="f_${fid}">`;
            storeList.forEach(s => {
                const sel = s.id === def.default ? 'selected' : '';
                html += `<option value="${s.id}" ${sel}>${s.name}(${s.id})</option>`;
            });
            html += `</select>`;
        } else if (fid === 'ccode' && REPORTS[currentReport].group === 'category') {
            html += `<select id="f_${fid}">
                <option value="">全部</option>
                <option value="11">生鲜</option>
                <option value="22">食品</option>
                <option value="33">非食品</option>
            </select>`;
        } else if (def.type === 'select' && def.options) {
            html += `<select id="f_${fid}">`;
            def.options.forEach(o => {
                const sel = o === def.default ? 'selected' : '';
                html += `<option value="${o}" ${sel}>${o}</option>`;
            });
            html += `</select>`;
        } else if (def.type === 'number') {
            html += `<input type="number" id="f_${fid}" value="${def.default}" style="width:80px">`;
        } else {
            html += `<input type="text" id="f_${fid}" value="${def.default}" placeholder="${def.placeholder||''}" style="width:100px">`;
        }
        html += `</div>`;
    });

    html += `<div style="align-self:flex-end"><button class="btn" onclick="loadReport()">查询</button></div>`;
    html += `<div style="align-self:flex-end"><button class="btn" onclick="exportCSV()" style="background:linear-gradient(135deg,#43a047,#2e7d32)">导出CSV</button></div>`;
    bar.innerHTML = html;
    initDatePickers();
}

function renderDateRangeGroup(startId, endId, label) {
    return `
    <div class="date-range-group">
        <div class="date-range-label">${label}</div>
        <div class="date-presets">
            <button class="preset-btn" onclick="applyPreset('yesterday','${startId}','${endId}')">昨天</button>
            <button class="preset-btn" onclick="applyPreset('today','${startId}','${endId}')">今天</button>
            <button class="preset-btn" onclick="applyPreset('7d','${startId}','${endId}')">近7天</button>
            <button class="preset-btn" onclick="applyPreset('30d','${startId}','${endId}')">近30天</button>
            <button class="preset-btn" onclick="applyPreset('thismonth','${startId}','${endId}')">本月</button>
            <button class="preset-btn" onclick="applyPreset('lastmonth','${startId}','${endId}')">上月</button>
        </div>
        <input type="text" id="range_${startId}" class="date-range-input" placeholder="点击选择日期范围" readonly>
        <input type="hidden" id="f_${startId}">
        <input type="hidden" id="f_${endId}">
    </div>`;
}

function initDatePickers() {
    document.querySelectorAll('[id^="range_"]').forEach(el => {
        const startId = el.id.replace('range_', '');
        const endId   = startId === 'start' ? 'end'
                      : startId === 'cmp_start' ? 'cmp_end'
                      : null;
        if (!endId) return;
        if (el._flatpickr) el._flatpickr.destroy();
        flatpickr(el, {
            mode: 'range', locale: 'zh', dateFormat: 'Y-m-d', disableMobile: true,
            onChange(dates) {
                if (dates.length === 2) {
                    document.getElementById('f_' + startId).value = flatpickr.formatDate(dates[0], 'Y-m-d');
                    document.getElementById('f_' + endId).value   = flatpickr.formatDate(dates[1], 'Y-m-d');
                }
            }
        });
    });
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

function saveState(reportId) {
    const report = REPORTS[reportId];
    if (!report) return;
    const filters = {};
    report.filters.forEach(fid => {
        const el = document.getElementById('f_' + fid);
        if (el) filters[fid] = el.value;
    });
    reportStates[reportId] = {
        filters,
        data: lastData.slice(),
        rowCount:  document.getElementById('rowCount').textContent,
        tableHTML: document.getElementById('tableWrap').innerHTML,
        hasChart:  !document.getElementById('chartArea').classList.contains('hidden')
    };
}

function restoreState(reportId) {
    const state  = reportStates[reportId];
    if (!state || !state.data.length) return false;
    const report = REPORTS[reportId];
    report.filters.forEach(fid => {
        if (['start', 'end', 'cmp_start', 'cmp_end'].includes(fid)) return;
        const el = document.getElementById('f_' + fid);
        if (el && state.filters[fid] !== undefined) el.value = state.filters[fid];
    });
    [['start', 'end'], ['cmp_start', 'cmp_end']].forEach(([startId, endId]) => {
        if (!report.filters.includes(startId)) return;
        const s = state.filters[startId];
        const e = state.filters[endId];
        if (!s || !e) return;
        const sEl = document.getElementById('f_' + startId);
        const eEl = document.getElementById('f_' + endId);
        if (sEl) sEl.value = s;
        if (eEl) eEl.value = e;
        const rangeEl = document.getElementById('range_' + startId);
        if (rangeEl && rangeEl._flatpickr) rangeEl._flatpickr.setDate([s, e]);
    });
    document.getElementById('reportTitle').textContent  = report.label;
    document.getElementById('rowCount').textContent     = state.rowCount;
    document.getElementById('tableWrap').innerHTML      = state.tableHTML;
    lastData = state.data;
    if (state.hasChart) {
        document.getElementById('chartArea').classList.remove('hidden');
        renderChart(reportId, state.data);
    } else {
        document.getElementById('chartArea').classList.add('hidden');
    }
    return true;
}

function clearContent() {
    document.getElementById('reportTitle').textContent = REPORTS[currentReport]?.label || '--';
    document.getElementById('rowCount').textContent    = '';
    document.getElementById('tableWrap').innerHTML     = '<div class="status-msg">请点击查询按钮</div>';
    document.getElementById('chartArea').classList.add('hidden');
}

function renderTable(data, columns) {
    const wrap = document.getElementById('tableWrap');
    if (!data || !data.length) {
        wrap.innerHTML = '<div class="status-msg">暂无数据</div>';
        return;
    }
    const hasStickyCol = columns.some(c => c.sticky);
    const idxClass = hasStickyCol ? ' sticky-col' : '';

    let html = '<table class="data-table"><thead><tr>';
    html += `<th class="${idxClass.trim()}">#</th>`;
    columns.forEach(c => {
        const cls = [c.fmt ? 'num' : '', c.sticky ? 'sticky-col' : ''].filter(Boolean).join(' ');
        html += `<th class="${cls}">${c.label}</th>`;
    });
    html += '</tr></thead><tbody>';
    data.forEach((row, i) => {
        const isSummary = row['时段'] === null && row['hours'] === null && i === data.length - 1;
        html += `<tr class="${isSummary?'summary-row':''}">`;
        html += `<td class="${idxClass.trim()}">${isSummary ? '合计' : i+1}</td>`;
        columns.forEach(c => {
            const cls = [c.fmt ? 'num' : '', c.sticky ? 'sticky-col' : ''].filter(Boolean).join(' ');
            const val = row[c.key];
            html += `<td class="${cls}">${fmtVal(val, c.fmt, c.colored)}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;

    // Calculate and apply left offsets for sticky columns after DOM insertion
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

// ============================================================
// Charts
// ============================================================
function renderChart(reportId, data) {
    const report = REPORTS[reportId];
    if (!report.chart || !data || !data.length) {
        document.getElementById('chartArea').classList.add('hidden');
        return;
    }
    document.getElementById('chartArea').classList.remove('hidden');
    const dom = document.getElementById('mainChart');
    let chart = echarts.getInstanceByDom(dom);
    if (chart) chart.dispose();
    chart = echarts.init(dom);

    if (report.chart === 'hourly_sale') {
        const hours = data.filter(r => r.hours !== null).map(r => r.hours);
        const sales = data.filter(r => r.hours !== null).map(r => r.sale || 0);
        const kl    = data.filter(r => r.hours !== null).map(r => r.kl || 0);
        chart.setOption({
            tooltip: { trigger: 'axis' },
            legend: { data: ['销售额','客流'], textStyle:{color:'#78909c'} },
            grid: { left:60, right:60, top:40, bottom:30 },
            xAxis: { type:'category', data:hours, axisLabel:{color:'#546e7a'} },
            yAxis: [
                { type:'value', name:'销售额', axisLabel:{color:'#546e7a'}, splitLine:{lineStyle:{color:'#1e3a5f44'}} },
                { type:'value', name:'客流',   axisLabel:{color:'#546e7a'}, splitLine:{show:false} }
            ],
            series: [
                { name:'销售额', type:'bar',  data:sales, itemStyle:{color:'#29b6f6'} },
                { name:'客流',   type:'line', yAxisIndex:1, data:kl, itemStyle:{color:'#ffa726'}, smooth:true }
            ]
        });
    } else if (report.chart === 'compare') {
        const hours   = data.filter(r => r['时段'] !== null).map(r => r['时段']);
        const sale    = data.filter(r => r['时段'] !== null).map(r => r['销售额'] || 0);
        const cmpSale = data.filter(r => r['时段'] !== null).map(r => r['对比销售额'] || 0);
        chart.setOption({
            tooltip: { trigger: 'axis' },
            legend: { data: ['本期销售','对比期销售'], textStyle:{color:'#78909c'} },
            grid: { left:60, right:20, top:40, bottom:30 },
            xAxis: { type:'category', data:hours, axisLabel:{color:'#546e7a'} },
            yAxis: { type:'value', axisLabel:{color:'#546e7a'}, splitLine:{lineStyle:{color:'#1e3a5f44'}} },
            series: [
                { name:'本期销售',   type:'bar', data:sale,    itemStyle:{color:'#29b6f6'} },
                { name:'对比期销售', type:'bar', data:cmpSale, itemStyle:{color:'#ffa72688'} }
            ]
        });
    } else if (report.chart === 'category_movement') {
        const names     = data.map(r => r['分类名称'] || r['分类号码']);
        const dongxiao  = data.map(r => r['动销数']   || 0);
        const budongxiao = data.map(r => r['不动销数'] || 0);
        chart.setOption({
            tooltip: { trigger: 'axis' },
            legend: { data: ['动销数','不动销数'], textStyle:{color:'#78909c'} },
            grid: { left:100, right:20, top:40, bottom:10 },
            xAxis: { type:'value', axisLabel:{color:'#546e7a'}, splitLine:{lineStyle:{color:'#1e3a5f44'}} },
            yAxis: { type:'category', data:names.slice(0,30), axisLabel:{color:'#b0bec5',fontSize:11} },
            series: [
                { name:'动销数',   type:'bar', data:dongxiao.slice(0,30),   stack:'a', itemStyle:{color:'#66bb6a'} },
                { name:'不动销数', type:'bar', data:budongxiao.slice(0,30), stack:'a', itemStyle:{color:'#ef5350'} }
            ]
        });
    }
    setTimeout(() => chart.resize(), 100);
}

// ============================================================
// Data loading
// ============================================================
async function loadReport() {
    const report = REPORTS[currentReport];
    if (!report) return;

    document.getElementById('reportTitle').textContent = report.label;
    document.getElementById('tableWrap').innerHTML     = '<div class="status-msg loading-spinner">加载中</div>';
    document.getElementById('chartArea').classList.add('hidden');

    const params = new URLSearchParams();
    report.filters.forEach(fid => {
        const el = document.getElementById('f_' + fid);
        if (el && el.value) params.set(fid, el.value);
    });
    if (report.group === 'category' && params.get('ccode')) {
        params.set('clevel', '2');
    }

    try {
        const url  = report.api + '?' + params.toString();
        const res  = await fetch(url);
        const json = await res.json();

        if (json.error) {
            document.getElementById('tableWrap').innerHTML = `<div class="status-msg error">查询出错: ${json.error}</div>`;
            document.getElementById('rowCount').textContent = '';
            return;
        }

        const rows = json.rows || json;
        lastData = rows;
        document.getElementById('rowCount').textContent = `共 ${rows.length} 条记录`;
        renderTable(rows, report.columns);
        renderChart(currentReport, rows);
        saveState(currentReport);
    } catch(e) {
        document.getElementById('tableWrap').innerHTML = `<div class="status-msg error">请求失败: ${e.message}</div>`;
    }
}

// ============================================================
// CSV Export
// ============================================================
function exportCSV() {
    const report = REPORTS[currentReport];
    if (!report || !lastData || !lastData.length) return;
    const cols = report.columns;
    let csv = '\uFEFF';
    csv += cols.map(c => c.label).join(',') + '\n';
    lastData.forEach(row => {
        csv += cols.map(c => {
            let v = row[c.key];
            if (v === null || v === undefined) return '';
            v = String(v).replace(/"/g, '""');
            return `"${v}"`;
        }).join(',') + '\n';
    });
    const blob = new Blob([csv], {type:'text/csv;charset=utf-8;'});
    const link = document.createElement('a');
    link.href     = URL.createObjectURL(blob);
    link.download = `${report.label}_${new Date().toISOString().slice(0,10)}.csv`;
    link.click();
}

// ============================================================
// Init
// ============================================================
function todayStr() {
    return new Date().toISOString().slice(0, 10);
}

async function init() {
    try {
        const res = await fetch('/api/stores');
        storeList = await res.json();
    } catch(e) {
        storeList = [{id:'11021', name:'默认门店'}];
    }

    document.querySelectorAll('#tabBar .tab').forEach(el => {
        el.addEventListener('click', () => {
            currentGroup = el.dataset.group;
            document.querySelectorAll('#tabBar .tab').forEach(t => t.classList.remove('active'));
            el.classList.add('active');
            currentReport = GROUPS[currentGroup].reports[0];
            renderSubTabs();
            renderFilters();
            if (!restoreState(currentReport)) clearContent();
        });
    });

    renderSubTabs();
    renderFilters();
    clearContent();

    if (currentReport === 't1') {
        const storeEl = document.getElementById('f_store');
        if (storeEl && T1_AUTO_STORE) {
            const match = storeList.find(s => s.name.includes(T1_AUTO_STORE));
            if (match) storeEl.value = match.id;
        }
        const dates = T1_TEST_DATES || { start: todayStr(), end: todayStr() };
        document.getElementById('f_start').value = dates.start;
        document.getElementById('f_end').value   = dates.end;
        const rangeEl = document.getElementById('range_start');
        if (rangeEl && rangeEl._flatpickr) {
            rangeEl._flatpickr.setDate([dates.start, dates.end]);
        }
        await loadReport();
    }
}

init();

window.addEventListener('resize', () => {
    const dom = document.getElementById('mainChart');
    if (dom) {
        const c = echarts.getInstanceByDom(dom);
        if (c) c.resize();
    }
});
