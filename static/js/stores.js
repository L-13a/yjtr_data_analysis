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

async function loadAll() {
    try {
        const [overview, storeRank, hourly] = await Promise.all([
            fetch('/api/overview').then(r => r.json()),
            fetch('/api/store_rank').then(r => r.json()),
            fetch('/api/hourly').then(r => r.json()),
        ]);

        document.getElementById('dataDate').textContent = overview.date;
        document.getElementById('refreshTime').textContent = new Date().toLocaleTimeString();

        if (typeof echarts === 'undefined') {
            document.querySelectorAll('.chart-container').forEach(el => {
                el.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#ef5350;font-size:14px;">图表库加载失败，请刷新页面重试</div>';
            });
        } else {
            try { renderHourly(hourly); } catch(e) { console.error('hourlyChart', e); }
            try { renderStoreRank(storeRank); } catch(e) { console.error('storeChart', e); }
        }

        setTimeout(resizeAllCharts, 100);
        setTimeout(resizeAllCharts, 500);
    } catch (e) {
        console.error('loadAll error:', e);
    }
}

loadAll();
setInterval(loadAll, 600000);
