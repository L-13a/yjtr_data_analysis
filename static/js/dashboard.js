const fmt = (n) => {
    if (n >= 10000) return (n / 10000).toFixed(2) + '万';
    return n.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
};
const fmtMoney = (n) => {
    if (Math.abs(n) >= 10000) return (n / 10000).toFixed(2) + '万';
    return n.toFixed(0);
};
const changeHtml = (val, suffix = '%') => {
    if (val === 0) return `<span style="color:#78909c">持平</span>`;
    const cls = val > 0 ? 'up' : 'down';
    const arrow = val > 0 ? '↑' : '↓';
    return `<span class="kpi-change ${cls}">较昨日 ${arrow} ${Math.abs(val).toFixed(1)}${suffix}</span>`;
};

// Theme colors
const colors = ['#4fc3f7', '#66bb6a', '#ffa726', '#ab47bc', '#ef5350', '#26c6da', '#ffca28', '#8d6e63', '#78909c', '#ec407a'];

// State for category drill-down
let categoryLevel = 1;        // 1=L1概览, 2=L2下钻
let currentL1 = null;         // 当前展开的L1品类名
let currentCategory = null;   // 时段客流图所选品类名
let currentCategoryCode = null; // 时段客流图所选L2 code (3位), null表示L1

const DRILLABLE_L1 = new Set(['生鲜', '食品', '非食品']);

function initChart(id) {
    const dom = document.getElementById(id);
    if (!dom || typeof echarts === 'undefined') return null;
    const existing = echarts.getInstanceByDom(dom);
    if (existing) existing.dispose();
    return echarts.init(dom, null, { renderer: 'canvas' });
}

// ========== Store filter ==========
async function loadStores() {
    try {
        const data = await fetch('/api/stores').then(r => r.json());
        const selectors = ['topProductsStoreFilter', 'categoryStoreFilter'];
        selectors.forEach(selId => {
            const sel = document.getElementById(selId);
            data.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s.id;
                opt.textContent = s.name;
                sel.appendChild(opt);
            });
        });
    } catch (e) { console.error('loadStores', e); }
}

async function loadTopProducts(storeId) {
    const url = storeId ? `/api/top_products?store_id=${encodeURIComponent(storeId)}` : '/api/top_products';
    const data = await fetch(url).then(r => r.json());
    renderTopProducts(data);
}

document.getElementById('topProductsStoreFilter').addEventListener('change', function () {
    loadTopProducts(this.value);
});

async function loadCategory(storeId) {
    if (categoryLevel === 2 && currentL1) {
        const url = `/api/category_l2?l1=${encodeURIComponent(currentL1)}` + (storeId ? `&store_id=${encodeURIComponent(storeId)}` : '');
        const data = await fetch(url).then(r => r.json());
        renderCategoryL2(data);
    } else {
        const url = storeId ? `/api/category?store_id=${encodeURIComponent(storeId)}` : '/api/category';
        const data = await fetch(url).then(r => r.json());
        renderCategory(data);
    }
    if (currentCategoryCode) {
        await loadCategoryHourly(currentCategory, storeId, currentCategoryCode);
    } else if (currentCategory) {
        await loadCategoryHourly(currentCategory, storeId);
    }
}

document.getElementById('categoryStoreFilter').addEventListener('change', function () {
    loadCategory(this.value);
});

// ========== Load Data ==========
async function loadAll() {
    try {
        document.getElementById('refreshTime', new Date().toLocaleTimeString());

        const [overview, trend, storeRank, category, hourly, topProducts, storeTrend] = await Promise.all([
            fetch('/api/overview').then(r => r.json()),
            fetch('/api/trend').then(r => r.json()),
            fetch('/api/store_rank').then(r => r.json()),
            fetch('/api/category').then(r => r.json()),
            fetch('/api/hourly').then(r => r.json()),
            fetch('/api/top_products').then(r => r.json()),
            fetch('/api/store_trend').then(r => r.json()),
        ]);

        document.getElementById('dataDate').textContent = overview.date;
        document.getElementById('refreshTime').textContent = new Date().toLocaleTimeString();

        document.getElementById('kpiSales').innerHTML = fmtMoney(overview.sales) + '<span class="kpi-unit">元</span>';
        document.getElementById('kpiSalesChange').innerHTML = changeHtml(overview.sales_change);
        document.getElementById('kpiProfit').innerHTML = fmtMoney(overview.profit) + '<span class="kpi-unit">元</span>';
        document.getElementById('kpiProfitChange').innerHTML = changeHtml(overview.profit_change);
        document.getElementById('kpiBills').innerHTML = fmt(overview.bills) + '<span class="kpi-unit">笔</span>';
        document.getElementById('kpiBillsChange').innerHTML = changeHtml(overview.bills_change);
        document.getElementById('kpiTicket').innerHTML = overview.avg_ticket.toFixed(1) + '<span class="kpi-unit">元</span>';
        document.getElementById('kpiTicketSub').innerHTML = changeHtml(overview.avg_ticket_change);
        document.getElementById('kpiProfitRate').innerHTML = overview.profit_rate.toFixed(1) + '<span class="kpi-unit">%</span>';
        document.getElementById('kpiMembers').innerHTML = changeHtml(overview.profit_rate_change, 'pp');

        renderTopProducts(topProducts);
        const renders = [
            ['trendChart',      () => renderTrend(trend)],
            ['storeChart',      () => renderStoreRank(storeRank)],
            ['categoryChart',   () => renderCategory(category)],
            ['hourlyChart',     () => renderHourly(hourly)],
            ['storeTrendChart', () => renderStoreTrend(storeTrend)],
        ];
        if (typeof echarts === 'undefined') {
            document.querySelectorAll('.chart-container').forEach(el => {
                el.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#ef5350;font-size:14px;">图表库加载失败，请刷新页面重试</div>';
            });
        } else {
            renders.forEach(([id, fn]) => { try { fn(); } catch (e) { console.error(id, e); } });
        }

        setTimeout(resizeAllCharts, 100);
        setTimeout(resizeAllCharts, 500);
    } catch (e) {
        console.error('loadAll error:', e);
    }
}

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
            {
                type: 'value', name: '金额', axisLabel: { color: '#546e7a', formatter: v => (v / 10000).toFixed(0) + '万' },
                splitLine: { lineStyle: { color: '#1e3a5f44' } }, nameTextStyle: { color: '#546e7a' }
            },
            {
                type: 'value', name: '笔数', axisLabel: { color: '#546e7a' },
                splitLine: { show: false }, nameTextStyle: { color: '#546e7a' }
            }
        ],
        series: [
            { name: '销售额', type: 'bar', data: data.sales, itemStyle: { color: '#29b6f6' }, barWidth: '35%' },
            {
                name: '毛利额', type: 'line', data: data.profit, lineStyle: { color: '#66bb6a', width: 2 },
                itemStyle: { color: '#66bb6a' }, symbol: 'circle', symbolSize: 4, smooth: true
            },
            {
                name: '交易笔数', type: 'line', yAxisIndex: 1, data: data.bills,
                lineStyle: { color: '#ffa726', width: 2, type: 'dashed' }, itemStyle: { color: '#ffa726' },
                symbol: 'none', smooth: true
            }
        ]
    });
}

function renderStoreRank(data) {
    const storeCount = data.stores.length;
    const el = document.getElementById('storeChart');
    el.style.height = Math.max(260, storeCount * 36 + 60) + 'px';

    const chart = initChart('storeChart');
    if (!chart) return;
    const stores = data.stores.slice().reverse();
    const sales  = data.sales.slice().reverse();
    const profit = data.profit.slice().reverse();
    chart.setOption({
        tooltip: {
            trigger: 'axis',
            formatter: p => p.map(i => `${i.marker} ${i.seriesName}: ${(i.value / 10000).toFixed(2)}万`).join('<br/>')
        },
        legend: { data: ['销售额', '毛利额'], textStyle: { color: '#78909c' }, top: 0 },
        grid: { left: 80, right: 20, top: 35, bottom: 10 },
        xAxis: {
            type: 'value', axisLabel: { color: '#546e7a', formatter: v => (v / 10000).toFixed(0) + '万' },
            splitLine: { lineStyle: { color: '#1e3a5f44' } }
        },
        yAxis: {
            type: 'category', data: stores, axisLabel: { color: '#b0bec5', fontSize: 11 },
            axisLine: { lineStyle: { color: '#1e3a5f' } }
        },
        series: [
            { name: '销售额', type: 'bar', data: sales,  itemStyle: { color: '#29b6f6' }, barWidth: '45%' },
            { name: '毛利额', type: 'bar', data: profit, itemStyle: { color: '#66bb6a' }, barWidth: '45%' }
        ]
    });
}

function renderCategory(data) {
    const chart = initChart('categoryChart');
    if (!chart) return;
    const pieData = data.categories.map((c, i) => ({
        name: c, value: data.sales[i], profit: data.profit[i]
    }));
    chart.setOption({
        tooltip: {
            formatter: p => `${p.name}<br/>销售: ${(p.value / 10000).toFixed(2)}万<br/>毛利: ${(p.data.profit / 10000).toFixed(2)}万<br/>占比: ${p.percent.toFixed(1)}%`
        },
        legend: { orient: 'horizontal', bottom: 0, textStyle: { color: '#78909c' } },
        series: [{
            type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'],
            label: { formatter: '{b}\n{d}%', color: '#b0bec5', fontSize: 12 },
            data: pieData,
            itemStyle: { borderColor: '#0f1923', borderWidth: 3 },
            color: ['#ef5350', '#ffa726', '#4fc3f7', '#66bb6a', '#78909c']
        }]
    });
    chart.off('click');
    chart.on('click', async function(params) {
        const name = params.name;
        const storeId = document.getElementById('categoryStoreFilter').value;
        if (DRILLABLE_L1.has(name)) {
            await drillDownCategory(name);
        } else {
            currentCategory = name;
            currentCategoryCode = null;
            await loadCategoryHourly(name, storeId);
        }
    });
}

async function loadCategoryHourly(category, storeId, ccode) {
    let url = ccode
        ? `/api/category_hourly?ccode=${encodeURIComponent(ccode)}`
        : `/api/category_hourly?category=${encodeURIComponent(category)}`;
    if (storeId) url += `&store_id=${encodeURIComponent(storeId)}`;
    try {
        const data = await fetch(url).then(r => r.json());
        renderCategoryHourly(data);
    } catch(e) {}
}

function renderCategoryHourly(data) {
    const el = document.getElementById('categoryHourlyChart');
    if (!el) return;
    el.innerHTML = '';
    const chart = initChart('categoryHourlyChart');
    if (!chart) return;
    document.getElementById('categoryHourlyTitle').innerHTML =
        `${data.category} · 各时段客流分布`;
    chart.setOption({
        tooltip: {
            trigger: 'axis',
            formatter: p => {
                let s = p[0].axisValue + '<br/>';
                p.forEach(i => {
                    const val = i.seriesName === '客流'
                        ? i.value + '笔'
                        : (i.value / 10000).toFixed(2) + '万元';
                    s += `${i.marker} ${i.seriesName}: ${val}<br/>`;
                });
                return s;
            }
        },
        legend: { data: ['客流', '销售额'], textStyle: { color: '#78909c' }, top: 0 },
        grid: { left: 55, right: 60, top: 35, bottom: 30 },
        xAxis: {
            type: 'category', data: data.hours, axisLabel: { color: '#546e7a' },
            axisLine: { lineStyle: { color: '#1e3a5f' } }
        },
        yAxis: [
            { type: 'value', name: '客流(笔)', axisLabel: { color: '#546e7a' }, splitLine: { lineStyle: { color: '#1e3a5f44' } }, nameTextStyle: { color: '#546e7a' } },
            { type: 'value', name: '销售额', axisLabel: { color: '#546e7a', formatter: v => (v / 10000).toFixed(1) + '万' }, splitLine: { show: false }, nameTextStyle: { color: '#546e7a' } }
        ],
        series: [
            {
                name: '客流', type: 'bar', data: data.bills,
                itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: '#66bb6a' }, { offset: 1, color: '#2e7d32' }
                ]) },
                barWidth: '50%'
            },
            {
                name: '销售额', type: 'line', yAxisIndex: 1, data: data.sales,
                lineStyle: { color: '#ffa726', width: 2 }, itemStyle: { color: '#ffa726' },
                symbol: 'circle', symbolSize: 4, smooth: true
            }
        ]
    });
}

function renderCategoryL2(data) {
    const chart = initChart('categoryChart');
    if (!chart) return;
    const pieData = data.categories.map((c, i) => ({
        name: c, value: data.sales[i], profit: data.profit[i], ccode: data.codes[i]
    }));
    chart.setOption({
        tooltip: {
            formatter: p => `${p.name}<br/>销售: ${(p.value / 10000).toFixed(2)}万<br/>毛利: ${(p.data.profit / 10000).toFixed(2)}万<br/>占比: ${p.percent.toFixed(1)}%`
        },
        legend: { orient: 'horizontal', bottom: 0, textStyle: { color: '#78909c' } },
        series: [{
            type: 'pie', radius: ['40%', '70%'], center: ['50%', '45%'],
            label: { formatter: '{b}\n{d}%', color: '#b0bec5', fontSize: 12 },
            data: pieData,
            itemStyle: { borderColor: '#0f1923', borderWidth: 3 },
            color: ['#4fc3f7', '#66bb6a', '#ffa726', '#ab47bc', '#ef5350',
                    '#26c6da', '#ffca28', '#8d6e63', '#78909c', '#ec407a']
        }]
    });
    chart.off('click');
    chart.on('click', async function(params) {
        currentCategory = params.name;
        currentCategoryCode = params.data.ccode;
        const storeId = document.getElementById('categoryStoreFilter').value;
        await loadCategoryHourly(currentCategory, storeId, currentCategoryCode);
    });
}

async function drillDownCategory(l1Name) {
    categoryLevel = 2;
    currentL1 = l1Name;
    currentCategory = l1Name;
    currentCategoryCode = null;
    document.getElementById('categoryChartTitle').textContent = '品类销售分布 · ' + l1Name;
    document.getElementById('categoryBackBtn').style.display = '';
    const storeId = document.getElementById('categoryStoreFilter').value;
    const url = `/api/category_l2?l1=${encodeURIComponent(l1Name)}` + (storeId ? `&store_id=${encodeURIComponent(storeId)}` : '');
    try {
        const data = await fetch(url).then(r => r.json());
        renderCategoryL2(data);
    } catch(e) { console.error('drillDownCategory', e); }
    await loadCategoryHourly(l1Name, storeId);
}

function drillUpCategory() {
    categoryLevel = 1;
    currentL1 = null;
    currentCategory = null;
    currentCategoryCode = null;
    document.getElementById('categoryChartTitle').textContent = '品类销售分布';
    document.getElementById('categoryBackBtn').style.display = 'none';
    document.getElementById('categoryHourlyTitle').innerHTML =
        '品类时段客流分布 <span style="color:#78909c;font-size:12px;font-weight:normal">（点击左侧环形图选择品类）</span>';
    const el = document.getElementById('categoryHourlyChart');
    const inst = echarts.getInstanceByDom(el);
    if (inst) inst.dispose();
    el.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#546e7a;font-size:14px;">点击左侧环形图选择品类</div>';
    const storeId = document.getElementById('categoryStoreFilter').value;
    loadCategory(storeId);
}

function renderHourly(data) {
    const chart = initChart('hourlyChart');
    if (!chart) return;
    chart.setOption({
        tooltip: {
            trigger: 'axis',
            formatter: p => {
                let s = p[0].axisValue + '<br/>';
                p.forEach(i => {
                    let val;
                    if (i.seriesName === '交易笔数') val = i.value + '笔';
                    else if (i.seriesName === '客单价') val = i.value.toFixed(2) + '元';
                    else val = i.value.toFixed(0) + '元';
                    s += `${i.marker} ${i.seriesName}: ${val}<br/>`;
                });
                return s;
            }
        },
        legend: { data: ['销售额', '交易笔数', '客单价'], textStyle: { color: '#78909c' }, top: 0 },
        grid: { left: 55, right: 115, top: 35, bottom: 30 },
        xAxis: {
            type: 'category', data: data.hours, axisLabel: { color: '#546e7a' },
            axisLine: { lineStyle: { color: '#1e3a5f' } }
        },
        yAxis: [
            {
                type: 'value', name: '销售额', axisLabel: { color: '#546e7a' },
                splitLine: { lineStyle: { color: '#1e3a5f44' } }, nameTextStyle: { color: '#546e7a' }
            },
            {
                type: 'value', name: '笔数', axisLabel: { color: '#546e7a' },
                splitLine: { show: false }, nameTextStyle: { color: '#546e7a' }
            },
            {
                type: 'value', name: '客单价', position: 'right', offset: 55,
                axisLabel: { color: '#ce93d8', formatter: v => v.toFixed(0) },
                splitLine: { show: false }, nameTextStyle: { color: '#ce93d8' },
                axisLine: { show: true, lineStyle: { color: '#ce93d8' } }
            }
        ],
        series: [
            {
                name: '销售额', type: 'bar', data: data.sales, itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: '#4fc3f7' }, { offset: 1, color: '#0277bd' }
                    ])
                }, barWidth: '50%'
            },
            {
                name: '交易笔数', type: 'line', yAxisIndex: 1, data: data.bills,
                lineStyle: { color: '#ffa726', width: 2 }, itemStyle: { color: '#ffa726' },
                symbol: 'circle', symbolSize: 4, smooth: true
            },
            {
                name: '客单价', type: 'line', yAxisIndex: 2, data: data.avg_ticket,
                lineStyle: { color: '#ce93d8', width: 2 }, itemStyle: { color: '#ce93d8' },
                symbol: 'circle', symbolSize: 4, smooth: true
            }
        ]
    });
}

function renderTopProducts(data) {
    const container = document.getElementById('topProducts');
    let html = '<table class="product-table"><thead><tr><th>#</th><th>商品</th><th>销售额</th><th>数量</th><th>毛利</th></tr></thead><tbody>';
    data.products.forEach((p, i) => {
        const rankCls  = i < 3 ? `rank-${i + 1}` : 'rank-n';
        const profitCls = data.profit[i] >= 0 ? 'profit-positive' : 'profit-negative';
        html += `<tr>
            <td><span class="rank-badge ${rankCls}">${i + 1}</span></td>
            <td>${p}</td>
            <td>${data.sales[i].toFixed(0)}</td>
            <td>${data.qty[i]}</td>
            <td class="${profitCls}">${data.profit[i].toFixed(0)}</td>
        </tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}

function renderPayment(data) {
    const chart = initChart('paymentChart');
    if (!chart) return;
    const pieData = data.types.map((t, i) => ({ name: t, value: data.amounts[i] }));
    chart.setOption({
        tooltip: { formatter: p => `${p.name}<br/>${(p.value / 10000).toFixed(2)}万元 (${p.percent.toFixed(1)}%)` },
        legend: { orient: 'vertical', right: 10, top: 'middle', textStyle: { color: '#78909c' } },
        series: [{
            type: 'pie', radius: ['45%', '72%'], center: ['40%', '50%'],
            label: { show: false },
            data: pieData,
            itemStyle: { borderColor: '#0f1923', borderWidth: 3 },
            color: ['#4fc3f7', '#66bb6a', '#ffa726', '#ab47bc', '#ef5350', '#78909c']
        }]
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
        xAxis: {
            type: 'category', data: data.dates.map(d => d.slice(5)),
            axisLabel: { color: '#546e7a' }, axisLine: { lineStyle: { color: '#1e3a5f' } }
        },
        yAxis: {
            type: 'value', axisLabel: { color: '#546e7a', formatter: v => (v / 10000).toFixed(0) + '万' },
            splitLine: { lineStyle: { color: '#1e3a5f44' } }
        },
        series: series
    });
}

// Responsive resize
function resizeAllCharts() {
    document.querySelectorAll('.chart-container').forEach(el => {
        const chart = echarts.getInstanceByDom(el);
        if (chart) chart.resize();
    });
}
window.addEventListener('resize', resizeAllCharts);
window.addEventListener('orientationchange', () => { setTimeout(resizeAllCharts, 300); });

// Load and auto-refresh
loadStores();
loadAll();
setInterval(loadAll, 600000);
