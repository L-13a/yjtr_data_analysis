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

async function loadOverview() {
    try {
        const overview = await fetch('/api/overview').then(r => r.json());

        document.getElementById('dataDate').textContent = overview.date;
        document.getElementById('refreshTime').textContent = new Date().toLocaleTimeString();

        document.getElementById('kpiSales').innerHTML = fmtMoney(overview.sales) + '<span class="kpi-unit">元</span>';
        document.getElementById('kpiSalesChange').innerHTML = changeHtml(overview.sales_change);
        document.getElementById('kpiProfit').innerHTML = fmtMoney(overview.profit) + '<span class="kpi-unit">元</span>';
        document.getElementById('kpiProfitChange').innerHTML = changeHtml(overview.profit_change);
        document.getElementById('kpiBills').innerHTML = (overview.bills >= 10000 ? (overview.bills / 10000).toFixed(2) + '万' : overview.bills) + '<span class="kpi-unit">笔</span>';
        document.getElementById('kpiBillsChange').innerHTML = changeHtml(overview.bills_change);
        document.getElementById('kpiTicket').innerHTML = overview.avg_ticket.toFixed(1) + '<span class="kpi-unit">元</span>';
        document.getElementById('kpiTicketSub').innerHTML = changeHtml(overview.avg_ticket_change);
        document.getElementById('kpiProfitRate').innerHTML = overview.profit_rate.toFixed(1) + '<span class="kpi-unit">%</span>';
        document.getElementById('kpiMembers').innerHTML = changeHtml(overview.profit_rate_change, 'pp');
    } catch (e) {
        console.error('loadOverview error:', e);
    }
}

loadOverview();
setInterval(loadOverview, 600000);
