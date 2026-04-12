async function loadStores() {
    try {
        const data = await fetch('/api/stores').then(r => r.json());
        const sel = document.getElementById('topProductsStoreFilter');
        data.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.id;
            opt.textContent = s.name;
            sel.appendChild(opt);
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

async function loadAll() {
    try {
        const [overview, topProducts] = await Promise.all([
            fetch('/api/overview').then(r => r.json()),
            fetch('/api/top_products').then(r => r.json()),
        ]);

        document.getElementById('dataDate').textContent = overview.date;
        document.getElementById('refreshTime').textContent = new Date().toLocaleTimeString();

        renderTopProducts(topProducts);
    } catch (e) {
        console.error('loadAll error:', e);
    }
}

loadStores();
loadAll();
setInterval(loadAll, 600000);
