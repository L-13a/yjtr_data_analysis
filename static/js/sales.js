// ============================================================
// 销售分析页 JS
// 依赖：report_utils.js（fmtVal, renderEmbedTable, applyPreset, initRangePicker）
// ============================================================

const colors = ['#4fc3f7','#66bb6a','#ffa726','#ab47bc','#ef5350','#26c6da','#ffca28','#8d6e63','#78909c','#ec407a'];

function initChart(id) {
    const dom = document.getElementById(id);
    if (!dom || typeof echarts === 'undefined') return null;
    const existing = echarts.getInstanceByDom(dom);
    if (existing) existing.dispose();
    return echarts.init(dom, null, { renderer: 'canvas' });
}

function resizeAllCharts() {
    document.querySelectorAll('.chart-container, #rptMainChart').forEach(el => {
        const chart = echarts.getInstanceByDom(el);
        if (chart) chart.resize();
    });
}
window.addEventListener('resize', resizeAllCharts);

// ============================================================
// 看板图表
// ============================================================
function renderTrend(data) {
    const chart = initChart('trendChart');
    if (!chart) return;
    chart.setOption({
        tooltip: {
            trigger: 'axis',
            formatter: function (params) {
                let s = params[0].axisValue + '<br/>';
                params.forEach(p => {
                    const val = p.seriesName === '交易笔数' ? p.value + '笔' : (p.value / 10000).toFixed(2) + '万元';
                    s += `${p.marker} ${p.seriesName}: ${val}<br/>`;
                });
                return s;
            }
        },
        legend: { data: ['销售额', '毛利额', '交易笔数'], textStyle: { color: '#78909c' }, top: 0 },
        grid: { left: 60, right: 60, top: 40, bottom: 30 },
        xAxis: {
            type: 'category', data: data.dates.map(d => d.slice(5)),
            axisLabel: { color: '#546e7a' }, axisLine: { lineStyle: { color: '#1e3a5f' } }
        },
        yAxis: [
            { type: 'value', name: '金额', axisLabel: { color: '#546e7a', formatter: v => (v / 10000).toFixed(0) + '万' }, splitLine: { lineStyle: { color: '#1e3a5f44' } }, nameTextStyle: { color: '#546e7a' } },
            { type: 'value', name: '笔数', axisLabel: { color: '#546e7a' }, splitLine: { show: false }, nameTextStyle: { color: '#546e7a' } }
        ],
        series: [
            { name: '销售额', type: 'bar', data: data.sales, itemStyle: { color: '#29b6f6' }, barWidth: '35%' },
            { name: '毛利额', type: 'line', data: data.profit, lineStyle: { color: '#66bb6a', width: 2 }, itemStyle: { color: '#66bb6a' }, symbol: 'circle', symbolSize: 4, smooth: true },
            { name: '交易笔数', type: 'line', yAxisIndex: 1, data: data.bills, lineStyle: { color: '#ffa726', width: 2, type: 'dashed' }, itemStyle: { color: '#ffa726' }, symbol: 'none', smooth: true }
        ]
    });
}

function renderStoreTrend(data) {
    const chart = initChart('storeTrendChart');
    if (!chart) return;
    const series = data.series.map((s, i) => ({
        name: s.name, type: 'line', data: s.data,
        lineStyle: { width: 2 }, symbol: 'circle', symbolSize: 4,
        smooth: true, itemStyle: { color: colors[i % colors.length] }
    }));
    chart.setOption({
        tooltip: {
            trigger: 'axis',
            formatter: params => {
                let s = params[0].axisValue + '<br/>';
                params.sort((a, b) => b.value - a.value).forEach(p => {
                    s += `${p.marker} ${p.seriesName}: ${(p.value / 10000).toFixed(2)}万<br/>`;
                });
                return s;
            }
        },
        legend: { type: 'scroll', bottom: 0, textStyle: { color: '#78909c', fontSize: 11 } },
        grid: { left: 55, right: 15, top: 10, bottom: 45 },
        xAxis: { type: 'category', data: data.dates.map(d => d.slice(5)), axisLabel: { color: '#546e7a' }, axisLine: { lineStyle: { color: '#1e3a5f' } } },
        yAxis: { type: 'value', axisLabel: { color: '#546e7a', formatter: v => (v / 10000).toFixed(0) + '万' }, splitLine: { lineStyle: { color: '#1e3a5f44' } } },
        series
    });
}

async function loadAll() {
    try {
        const [overview, trend, storeTrend] = await Promise.all([
            fetch('/api/overview').then(r => r.json()),
            fetch('/api/trend').then(r => r.json()),
            fetch('/api/store_trend').then(r => r.json()),
        ]);

        document.getElementById('dataDate').textContent = overview.date;
        document.getElementById('refreshTime').textContent = new Date().toLocaleTimeString();

        if (typeof echarts === 'undefined') {
            document.querySelectorAll('.chart-container').forEach(el => {
                el.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#ef5350;font-size:14px;">图表库加载失败，请刷新页面重试</div>';
            });
        } else {
            try { renderTrend(trend); } catch(e) { console.error('trendChart', e); }
            try { renderStoreTrend(storeTrend); } catch(e) { console.error('storeTrendChart', e); }
        }
        setTimeout(resizeAllCharts, 100);
        setTimeout(resizeAllCharts, 500);
    } catch (e) {
        console.error('loadAll error:', e);
    }
}

// ============================================================
// 嵌入报表：T1 / T2 / T4
// ============================================================
const SALES_REPORTS = {
    t1: {
        label: 'T1 销售客单按时段',
        api: '/api/t1_sale_bytime',
        columns: [
            {key:'c_store_name',label:'门店'},{key:'c_ccode_name',label:'品类'},
            {key:'hours',label:'时段'},{key:'kl',label:'客流',fmt:'int'},
            {key:'kd',label:'客单',fmt:'money'},{key:'sale',label:'销售额',fmt:'money'},
            {key:'salesum',label:'累计销售',fmt:'money'}
        ],
        chart: 'hourly_sale'
    },
    t2: {
        label: 'T2 总客流日报',
        api: '/api/daily_flow',
        dataKey: 'rows',
        columns: [
            {key:'date',label:'日期'},{key:'weekday',label:'星期'},{key:'store_name',label:'机构'},
            {key:'flow_count',label:'客流',fmt:'int'},{key:'avg_ticket',label:'客单',fmt:'money'},
            {key:'sales',label:'销售额',fmt:'money'},{key:'profit',label:'毛利额',fmt:'money'},
            {key:'profit_rate',label:'毛利率',fmt:'pct'}
        ]
    },
    t4: {
        label: 'T4 销售时段对比',
        api: '/api/t4_sale_compare',
        hasCompare: true,
        columns: [
            {key:'时段',label:'时段'},{key:'销售额',label:'销售额',fmt:'money'},{key:'客流',label:'客流',fmt:'int'},
            {key:'客单',label:'客单',fmt:'money'},{key:'对比销售额',label:'对比销售额',fmt:'money'},
            {key:'对比客流',label:'对比客流',fmt:'int'},{key:'对比客单',label:'对比客单',fmt:'money'},
            {key:'销售差',label:'销售差',fmt:'money',colored:true},{key:'销售对比率',label:'销售对比率',fmt:'pct'},
            {key:'客流差',label:'客流差',fmt:'int',colored:true},{key:'客单差',label:'客单差',fmt:'money',colored:true}
        ],
        chart: 'compare'
    }
};

let currentSalesReport = null;
let salesStoreList = [];
let salesLastData = [];

async function loadSalesStores() {
    try {
        salesStoreList = await fetch('/api/stores').then(r => r.json());
    } catch(e) {
        salesStoreList = [{id:'11021', name:'默认门店'}];
    }
}

function openReport(reportId) {
    currentSalesReport = reportId;
    salesLastData = [];

    // 更新图标激活状态
    document.querySelectorAll('#rptTabRow .rpt-shortcut').forEach(el => {
        el.classList.toggle('active', el.dataset.report === reportId);
    });

    // 展开内容区
    document.getElementById('rptPanel').style.display = 'block';

    // 渲染筛选栏
    renderSalesFilterBar(reportId);

    // 清空内容
    document.getElementById('rptChartArea').classList.add('hidden');
    document.getElementById('rptTableWrap').innerHTML = '<div class="status-msg">请点击查询按钮</div>';
    document.getElementById('rptRowCount').textContent = '';
}

function renderSalesFilterBar(reportId) {
    const report = SALES_REPORTS[reportId];
    const bar = document.getElementById('rptFilterBar');

    let storeOpts = salesStoreList.map(s => `<option value="${s.id}">${s.name}(${s.id})</option>`).join('');
    const storeHtml = `<div><label>机构</label><select id="f_store">${storeOpts}</select></div>`;

    const dateHtml = `
        <div class="date-range-group">
            <div class="date-range-label">查询区间</div>
            <div class="date-presets">
                <button class="preset-btn" onclick="applyPreset('yesterday','start','end')">昨天</button>
                <button class="preset-btn" onclick="applyPreset('today','start','end')">今天</button>
                <button class="preset-btn" onclick="applyPreset('7d','start','end')">近7天</button>
                <button class="preset-btn" onclick="applyPreset('30d','start','end')">近30天</button>
                <button class="preset-btn" onclick="applyPreset('thismonth','start','end')">本月</button>
                <button class="preset-btn" onclick="applyPreset('lastmonth','start','end')">上月</button>
            </div>
            <input type="text" id="range_start" class="date-range-input" placeholder="点击选择日期范围" readonly>
            <input type="hidden" id="f_start">
            <input type="hidden" id="f_end">
        </div>`;

    const cmpHtml = report.hasCompare ? `
        <div class="date-range-group">
            <div class="date-range-label">对比区间</div>
            <div class="date-presets">
                <button class="preset-btn" onclick="applyPreset('yesterday','cmp_start','cmp_end')">昨天</button>
                <button class="preset-btn" onclick="applyPreset('7d','cmp_start','cmp_end')">近7天</button>
                <button class="preset-btn" onclick="applyPreset('lastmonth','cmp_start','cmp_end')">上月</button>
            </div>
            <input type="text" id="range_cmp_start" class="date-range-input" placeholder="点击选择对比日期范围" readonly>
            <input type="hidden" id="f_cmp_start">
            <input type="hidden" id="f_cmp_end">
        </div>` : '';

    const btnHtml = `
        <div style="display:flex;gap:8px;">
            <button class="query-btn" onclick="querySalesReport()">查询</button>
            <button class="export-btn" onclick="exportSalesCSV()">导出 CSV</button>
        </div>`;

    bar.innerHTML = storeHtml + dateHtml + cmpHtml + btnHtml;

    initRangePicker('start', 'end');
    if (report.hasCompare) initRangePicker('cmp_start', 'cmp_end');
}

async function querySalesReport() {
    const report = SALES_REPORTS[currentSalesReport];
    if (!report) return;

    document.getElementById('rptTableWrap').innerHTML = '<div class="status-msg loading-spinner">加载中</div>';
    document.getElementById('rptChartArea').classList.add('hidden');
    document.getElementById('rptRowCount').textContent = '';

    const params = new URLSearchParams();
    const get = id => { const el = document.getElementById(id); return el ? el.value : ''; };

    if (get('f_store'))     params.set('store', get('f_store'));
    if (get('f_start'))     params.set('start', get('f_start'));
    if (get('f_end'))       params.set('end',   get('f_end'));
    if (report.hasCompare) {
        if (get('f_cmp_start')) params.set('cmp_start', get('f_cmp_start'));
        if (get('f_cmp_end'))   params.set('cmp_end',   get('f_cmp_end'));
    }

    try {
        const json = await fetch(report.api + '?' + params).then(r => r.json());
        if (json.error) {
            document.getElementById('rptTableWrap').innerHTML = `<div class="status-msg error">查询出错: ${json.error}</div>`;
            return;
        }
        const rows = report.dataKey ? json[report.dataKey] : (json.rows || json);
        salesLastData = rows;
        document.getElementById('rptRowCount').textContent = `共 ${rows.length} 条记录`;
        renderEmbedTable('rptTableWrap', rows, report.columns);
        renderSalesChart(currentSalesReport, rows);
    } catch(e) {
        document.getElementById('rptTableWrap').innerHTML = `<div class="status-msg error">请求失败: ${e.message}</div>`;
    }
}

function renderSalesChart(reportId, data) {
    const report = SALES_REPORTS[reportId];
    const chartArea = document.getElementById('rptChartArea');
    if (!report.chart || !data || !data.length) { chartArea.classList.add('hidden'); return; }
    chartArea.classList.remove('hidden');

    const dom = document.getElementById('rptMainChart');
    const existing = echarts.getInstanceByDom(dom);
    if (existing) existing.dispose();
    const chart = echarts.init(dom);

    if (reportId === 't1') {
        const rows = data.filter(r => r.hours !== null);
        chart.setOption({
            tooltip: { trigger: 'axis' },
            legend: { data: ['销售额', '客流'], textStyle: { color: '#78909c' } },
            grid: { left: 60, right: 60, top: 40, bottom: 30 },
            xAxis: { type: 'category', data: rows.map(r => r.hours), axisLabel: { color: '#546e7a' }, axisLine: { lineStyle: { color: '#1e3a5f' } } },
            yAxis: [
                { type: 'value', name: '销售额', axisLabel: { color: '#546e7a' }, splitLine: { lineStyle: { color: '#1e3a5f44' } } },
                { type: 'value', name: '客流',   axisLabel: { color: '#546e7a' }, splitLine: { show: false } }
            ],
            series: [
                { name: '销售额', type: 'bar',  data: rows.map(r => r.sale || 0), itemStyle: { color: '#29b6f6' } },
                { name: '客流',   type: 'line', yAxisIndex: 1, data: rows.map(r => r.kl || 0), itemStyle: { color: '#ffa726' }, smooth: true }
            ]
        });
    } else if (reportId === 't4') {
        const rows = data.filter(r => r['时段'] !== null);
        chart.setOption({
            tooltip: { trigger: 'axis' },
            legend: { data: ['本期销售', '对比期销售'], textStyle: { color: '#78909c' } },
            grid: { left: 60, right: 20, top: 40, bottom: 30 },
            xAxis: { type: 'category', data: rows.map(r => r['时段']), axisLabel: { color: '#546e7a' }, axisLine: { lineStyle: { color: '#1e3a5f' } } },
            yAxis: { type: 'value', axisLabel: { color: '#546e7a' }, splitLine: { lineStyle: { color: '#1e3a5f44' } } },
            series: [
                { name: '本期销售',   type: 'bar', data: rows.map(r => r['销售额'] || 0),    itemStyle: { color: '#29b6f6' } },
                { name: '对比期销售', type: 'bar', data: rows.map(r => r['对比销售额'] || 0), itemStyle: { color: '#ffa72688' } }
            ]
        });
    }
    setTimeout(() => chart.resize(), 100);
}

function exportSalesCSV() {
    const report = SALES_REPORTS[currentSalesReport];
    if (!report || !salesLastData.length) return;
    let csv = '\uFEFF' + report.columns.map(c => c.label).join(',') + '\n';
    salesLastData.forEach(row => {
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

// ============================================================
// Init
// ============================================================
loadSalesStores();
loadAll();
setInterval(loadAll, 600000);
