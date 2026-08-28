// Function to update dashboard cards dynamically

function updateDashboardCards(data) {
    if (!data || !data.current_stats) return;

    const stats = data.current_stats;

    // Update New Customers
    const newCustomersCount = document.getElementById('newCustomersCount');
    const newCustomersChange = document.getElementById('newCustomersChange');
    if (newCustomersCount) newCustomersCount.textContent = stats.new_customers ?? '0';
    if (newCustomersChange) newCustomersChange.innerHTML = `<i class="ti ti-arrow-up-right"></i> N/A`;

    // Update Orders
    const ordersCount = document.getElementById('ordersCount');
    const ordersChange = document.getElementById('ordersChange');
    if (ordersCount) ordersCount.textContent = stats.orders ?? '0';
    if (ordersChange) ordersChange.innerHTML = `<i class="ti ti-arrow-up-right"></i> N/A`;

    // Update Completed
    const completedCount = document.getElementById('completedCount');
    const completedChange = document.getElementById('completedChange');
    if (completedCount) completedCount.textContent = stats.completed ?? '0';
    if (completedChange) completedChange.innerHTML = `<i class="ti ti-arrow-up-right"></i> N/A`;

    // Update Cancelled
    const cancelledCount = document.getElementById('cancelledCount');
    const cancelledChange = document.getElementById('cancelledChange');
    if (cancelledCount) cancelledCount.textContent = stats.cancelled ?? '0';
    if (cancelledChange) cancelledChange.innerHTML = `<i class="ti ti-arrow-up-right"></i> N/A`;

    // Update Refund Requests
    const refundRequestCount = document.getElementById('refundRequestCount');
    const refundRequestChange = document.getElementById('refundRequestChange');
    if (refundRequestCount) refundRequestCount.textContent = stats.refund_requests ?? '0';
    if (refundRequestChange) refundRequestChange.innerHTML = `<i class="ti ti-arrow-up-right"></i> N/A`;
}

function updateStockReportTable(data) {
    if (!data || !data.stock_report) return;
    const tbody = document.querySelector('table.table tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    data.stock_report.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><input type="checkbox"></td>
            <td>${item.items}</td>
            <td>${item.product_id}</td>
            <td>$${item.price}</td>
            <td>${item.category}</td>
            <td>${item.quantity}</td>
            <td><span class="badge bg-${item.status === 'In stock' ? 'success' : 'danger'}">${item.status}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function updateTopSellingProductsTable(data) {
    if (!data || !data.top_selling_products) return;
    const tbody = document.querySelectorAll('table.table')[1]?.querySelector('tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    data.top_selling_products.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.date}</td>
            <td>${item.items}</td>
            <td>${item.product_id}</td>
            <td>$${item.price}</td>
            <td>${item.sales}</td>
            <td>$${item.earnings}</td>
        `;
        tbody.appendChild(tr);
    });
}

function renderTotalSalesChart(data) {
    if (!data || !data.weekly_earnings) return;
    const options = {
        chart: {
            type: 'bar',
            height: 200,
        },
        series: [{
            name: 'Total Sales',
            data: data.weekly_earnings.map(item => item.total)
        }],
        xaxis: {
            categories: data.weekly_earnings.map(item => item.day)
        }
    };
    const chart = new ApexCharts(document.querySelector("#totalSalesGauge"), options);
    chart.render();
}

function renderSalesPerformanceChart(data) {
    if (!data || !data.sales_expenses) return;
    const options = {
        chart: {
            type: 'line',
            height: 200,
        },
        series: [
            {
                name: 'Sales',
                data: data.sales_expenses.sales
            },
            {
                name: 'Expenses',
                data: data.sales_expenses.expenses
            }
        ],
        xaxis: {
            categories: data.sales_expenses.dates
        }
    };
    const chart = new ApexCharts(document.querySelector("#salesPerformanceChart"), options);
    chart.render();
}

// Fetch dashboard data and update cards, tables, and charts on page load
document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/dashboard/')
        .then(response => response.json())
        .then(data => {
            updateDashboardCards(data);
            renderTotalSalesChart(data);
            renderSalesPerformanceChart(data);
        })
        .catch(error => {
            console.error('Error fetching dashboard data:', error);
        });

    fetch('/api/stock_report/')
        .then(response => response.json())
        .then(data => {
            updateStockReportTable(data);
        })
        .catch(error => {
            console.error('Error fetching stock report data:', error);
        });

    fetch('/api/top_selling_products/')
        .then(response => response.json())
        .then(data => {
            updateTopSellingProductsTable(data);
        })
        .catch(error => {
            console.error('Error fetching top selling products data:', error);
        });
});

 // Fetch dashboard data and update cards and tables on page load
 document.addEventListener('DOMContentLoaded', () => {
     fetch('/api/dashboard/')
         .then(response => response.json())
         .then(data => {
             updateDashboardCards(data);
         })
         .catch(error => {
             console.error('Error fetching dashboard data:', error);
         });

     fetch('/api/stock_report/')
         .then(response => response.json())
         .then(data => {
             updateStockReportTable(data);
         })
         .catch(error => {
             console.error('Error fetching stock report data:', error);
         });

    fetch('/api/top_selling_products/')
        .then(response => response.json())
        .then(data => {
            updateTopSellingProductsTable(data);
        })
        .catch(error => {
            console.error('Error fetching top selling products data:', error);
        });
});
