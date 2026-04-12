// ============================================================
// 供应链页 JS
// 依赖：report_utils.js（fmtVal, renderEmbedTable, applyPreset, initRangePicker）
// ============================================================

const SUPPLY_REPORTS = {
    t7: {
        label: 'T7 供应商到货率',
        api: '/api/t7_supplier_delivery',
        hasSupplier: true,
        columns: [
            {key:'供应商号',   label:'供应商号',   sticky: true},
            {key:'供应商名称', label:'供应商名称', sticky: true},
            {key:'销售额',    label:'销售额',    fmt:'money'},
            {key:'毛利',      label:'毛利',      fmt:'money'},
            {key:'毛利率',    label:'毛利率',    fmt:'pct'},
            {key:'品项数',    label:'品项数',    fmt:'int'},
            {key:'动销数',    label:'动销数',    fmt:'int'},
            {key:'动销率',    label:'动销率',    fmt:'pct'},
            {key:'订货量',    label:'订货量',    fmt:'num'},
            {key:'订货额',    label:'订货额',    fmt:'money'},
            {key:'到货量',    label:'到货量',    fmt:'num'},
            {key:'到货额',    label:'到货额',    fmt:'money'},
            {key:'到货量率',  label:'到货量率',  fmt:'pct'},
            {key:'到货额率',  label:'到货额率',  fmt:'pct'},
        ]
    },
    t11: {
        label: 'T11.1 供应商动销率',
        api: '/api/t11_supplier_movement',
        hasSupplier: true,
        hasCcode: true,
        columns: [
            {key:'机构',      label:'机构'},
            {key:'机构名称',  label:'机构名称'},
            {key:'供应商号',  label:'供应商号'},
            {key:'供应商名称',label:'供应商名称'},
            {key:'单品数',    label:'单品数',  fmt:'int'},
            {key:'动销数',    label:'动销数',  fmt:'int'},
            {key:'不动销数',  label:'不动销数',fmt:'int'},
            {key:'动销率',    label:'动销率',  fmt:'pct'},
        ]
    }
};

let currentSupplyReport = null;
let supplyStoreList = [];
let supplyLastData = [];

async function loadSupplyStores() {
    try {
        const res = await fetch('/api/overview');
        const ov = await res.json();
        document.getElementById('dataDate').textContent = ov.date;
        document.getElementById('refreshTime').textContent = new Date().toLocaleTimeString();
    } catch(e) {}
    try {
        supplyStoreList = await fetch('/api/stores').then(r => r.json());
    } catch(e) {
        supplyStoreList = [{id:'11021', name:'默认门店'}];
    }
}

function openReport(reportId) {
    currentSupplyReport = reportId;
    supplyLastData = [];

    document.querySelectorAll('#rptTabRow .rpt-shortcut').forEach(el => {
        el.classList.toggle('active', el.dataset.report === reportId);
    });

    document.getElementById('rptPanel').style.display = 'block';
    renderSupplyFilterBar(reportId);

    document.getElementById('rptTableWrap').innerHTML = '<div class="status-msg">请点击查询按钮</div>';
    document.getElementById('rptRowCount').textContent = '';
}

function renderSupplyFilterBar(reportId) {
    const report = SUPPLY_REPORTS[reportId];
    const bar = document.getElementById('rptFilterBar');

    const storeOpts = supplyStoreList.map(s => `<option value="${s.id}">${s.name}(${s.id})</option>`).join('');
    const storeHtml = `<div><label>机构</label><select id="f_store">${storeOpts}</select></div>`;

    const dateHtml = `
        <div class="date-range-group">
            <div class="date-range-label">查询区间</div>
            <div class="date-presets">
                <button class="preset-btn" onclick="applyPreset('yesterday','start','end')">昨天</button>
                <button class="preset-btn" onclick="applyPreset('7d','start','end')">近7天</button>
                <button class="preset-btn" onclick="applyPreset('30d','start','end')">近30天</button>
                <button class="preset-btn" onclick="applyPreset('thismonth','start','end')">本月</button>
                <button class="preset-btn" onclick="applyPreset('lastmonth','start','end')">上月</button>
            </div>
            <input type="text" id="range_start" class="date-range-input" placeholder="点击选择日期范围" readonly>
            <input type="hidden" id="f_start">
            <input type="hidden" id="f_end">
        </div>`;

    const supplierHtml = `
        <div>
            <label>供应商编码</label>
            <input type="text" id="f_supplier" placeholder="留空查全部" style="width:120px;">
        </div>`;

    const ccodeHtml = report.hasCcode ? `
        <div>
            <label>品类编码</label>
            <input type="text" id="f_ccode" placeholder="如 11" style="width:90px;">
        </div>` : '';

    const btnHtml = `
        <div style="display:flex;gap:8px;">
            <button class="query-btn" onclick="querySupplyReport()">查询</button>
            <button class="export-btn" onclick="exportSupplyCSV()">导出 CSV</button>
        </div>`;

    bar.innerHTML = storeHtml + dateHtml + supplierHtml + ccodeHtml + btnHtml;
    initRangePicker('start', 'end');
}

async function querySupplyReport() {
    const report = SUPPLY_REPORTS[currentSupplyReport];
    if (!report) return;

    document.getElementById('rptTableWrap').innerHTML = '<div class="status-msg loading-spinner">加载中</div>';
    document.getElementById('rptRowCount').textContent = '';

    const params = new URLSearchParams();
    const get = id => { const el = document.getElementById(id); return el ? el.value.trim() : ''; };

    if (get('f_store'))    params.set('store',    get('f_store'));
    if (get('f_start'))    params.set('start',    get('f_start'));
    if (get('f_end'))      params.set('end',      get('f_end'));
    if (get('f_supplier')) params.set('supplier', get('f_supplier'));
    if (report.hasCcode && get('f_ccode')) params.set('ccode', get('f_ccode'));

    try {
        const json = await fetch(report.api + '?' + params).then(r => r.json());
        if (json.error) {
            document.getElementById('rptTableWrap').innerHTML = `<div class="status-msg error">查询出错: ${json.error}</div>`;
            return;
        }
        const rows = json.rows || json;
        supplyLastData = rows;
        document.getElementById('rptRowCount').textContent = `共 ${rows.length} 条记录`;
        renderEmbedTable('rptTableWrap', rows, report.columns);
    } catch(e) {
        document.getElementById('rptTableWrap').innerHTML = `<div class="status-msg error">请求失败: ${e.message}</div>`;
    }
}

function exportSupplyCSV() {
    const report = SUPPLY_REPORTS[currentSupplyReport];
    if (!report || !supplyLastData.length) return;
    let csv = '\uFEFF' + report.columns.map(c => c.label).join(',') + '\n';
    supplyLastData.forEach(row => {
        csv += report.columns.map(c => {
            let v = row[c.key];
            if (v === null || v === undefined) return '';
            return `"${String(v).replace(/"/g, '""')}"`;
        }).join(',') + '\n';
    });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(new Blob([csv], {type:'text/csv;charset=utf-8;'}));
    link.download = `${report.label}_${new Date().toISOString().slice(0,10)}.csv`;
    link.click();
}

loadSupplyStores();
