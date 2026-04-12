let categoryLevel = 1;
let currentL1 = null;
let currentCategory = null;
let currentCategoryCode = null;

const DRILLABLE_L1 = new Set(['生鲜', '食品', '非食品']);

function initChart(id) {
    const dom = document.getElementById(id);
    if (!dom || typeof echarts === 'undefined') return null;
    const existing = echarts.getInstanceByDom(dom);
    if (existing) existing.dispose();
    return echarts.init(dom, null, { renderer: 'canvas' });
}

function resizeAllCharts() {
    document.querySelectorAll('.chart-container').forEach(el => {
        const chart = echarts.getInstanceByDom(el);
        if (chart) chart.resize();
    });
}
window.addEventListener('resize', resizeAllCharts);

async function loadStores() {
    try {
        const data = await fetch('/api/stores').then(r => r.json());
        const sel = document.getElementById('categoryStoreFilter');
        data.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.id;
            opt.textContent = s.name;
            sel.appendChild(opt);
        });
    } catch (e) { console.error('loadStores', e); }
}

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

function renderCategoryHourly(data) {
    const el = document.getElementById('categoryHourlyChart');
    if (!el) return;
    el.innerHTML = '';
    const chart = initChart('categoryHourlyChart');
    if (!chart) return;
    document.getElementById('categoryHourlyTitle').innerHTML = `${data.category} · 各时段客流分布`;
    chart.setOption({
        tooltip: {
            trigger: 'axis',
            formatter: p => {
                let s = p[0].axisValue + '<br/>';
                p.forEach(i => {
                    const val = i.seriesName === '客流' ? i.value + '笔' : (i.value / 10000).toFixed(2) + '万元';
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
                ]) }, barWidth: '50%'
            },
            {
                name: '销售额', type: 'line', yAxisIndex: 1, data: data.sales,
                lineStyle: { color: '#ffa726', width: 2 }, itemStyle: { color: '#ffa726' },
                symbol: 'circle', symbolSize: 4, smooth: true
            }
        ]
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

async function loadAll() {
    try {
        const [overview, category] = await Promise.all([
            fetch('/api/overview').then(r => r.json()),
            fetch('/api/category').then(r => r.json()),
        ]);

        document.getElementById('dataDate').textContent = overview.date;
        document.getElementById('refreshTime').textContent = new Date().toLocaleTimeString();

        if (typeof echarts === 'undefined') {
            document.querySelectorAll('.chart-container').forEach(el => {
                el.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#ef5350;font-size:14px;">图表库加载失败，请刷新页面重试</div>';
            });
        } else {
            try { renderCategory(category); } catch(e) { console.error('categoryChart', e); }
        }

        setTimeout(resizeAllCharts, 100);
        setTimeout(resizeAllCharts, 500);
    } catch (e) {
        console.error('loadAll error:', e);
    }
}

loadStores();
loadAll();
setInterval(loadAll, 600000);
