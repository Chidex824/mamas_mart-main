// Store chart instances globally
let dashboardCharts = {
    profit: null,
    breakup: null,
    earning: null
};

// Function to fetch dashboard data
async function fetchDashboardData() {
    try {
        const response = await fetch('/main/api/dashboard/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        });
        if (!response.ok) throw new Error('Network response was not ok');
        return await response.json();
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
        throw error;
    }
}

// Function to update dashboard stats
function updateDashboardStats(data) {
    const stats = data.current_stats;
    
    // Update total products
    const totalProductsEl = document.getElementById('totalProducts');
    if (totalProductsEl) totalProductsEl.textContent = stats.total_products;
    
    // Update low stock alerts
    const lowStockEl = document.getElementById('lowStockAlerts');
    if (lowStockEl) lowStockEl.textContent = stats.low_stock_products;
    
    // Update today's sales
    const todaySalesEl = document.getElementById('todaysSales');
    if (todaySalesEl) {
        todaySalesEl.textContent = `$${stats.todays_sales.total_sales || '0.00'}`;
        const transactionsEl = document.getElementById('todaysTransactions');
        if (transactionsEl) transactionsEl.textContent = stats.todays_sales.total_transactions || '0';
    }
}

// Function to safely initialize a chart
function initializeChart(containerId, config) {
    return new Promise((resolve, reject) => {
        const waitForContainer = () => {
            const container = document.getElementById(containerId);
            if (!container) {
                console.log(`Waiting for container #${containerId}...`);
                setTimeout(waitForContainer, 100);
                return;
            }

            console.log(`Container #${containerId} found, initializing chart...`);
            container.innerHTML = '';
            
            try {
                container.style.minHeight = '200px';
                container.style.width = '100%';
                
                const chart = new ApexCharts(container, {
                    ...config,
                    chart: {
                        ...config.chart,
                        background: 'transparent',
                        animations: {
                            enabled: true,
                            easing: 'easeinout',
                            speed: 800,
                            animateGradually: {
                                enabled: true,
                                delay: 150
                            },
                            dynamicAnimation: {
                                enabled: true,
                                speed: 350
                            }
                        },
                        toolbar: {
                            show: true,
                            tools: {
                                download: true,
                                selection: true,
                                zoom: true,
                                zoomin: true,
                                zoomout: true,
                                pan: true,
                                reset: true
                            }
                        },
                        events: {
                            error: function(e, ctx) {
                                console.error(`Chart error in ${containerId}:`, e);
                            }
                        }
                    }
                });

                chart.render()
                    .then(() => {
                        console.log(`Chart ${containerId} initialized successfully`);
                        resolve(chart);
                    })
                    .catch(e => {
                        console.warn(`Failed to render chart ${containerId}:`, e);
                        try {
                            chart.destroy();
                        } catch (destroyErr) {
                            console.warn('Error during chart cleanup:', destroyErr);
                        }
                        resolve(null);
                    });
            } catch (e) {
                console.error(`Error creating chart ${containerId}:`, e);
                resolve(null);
            }
        };

        waitForContainer();
    });
}

// Function to update chart data
function updateChartData(chart, newData) {
    if (!chart) return;
    
    try {
        chart.updateSeries(newData.series);
        if (newData.labels) {
            chart.updateOptions({
                labels: newData.labels,
                xaxis: { ...chart.opts.xaxis, categories: newData.labels }
            });
        }
    } catch (error) {
        console.error('Error updating chart:', error);
    }
}

// Function to initialize all dashboard charts
async function initializeDashboardCharts() {
    const dashboardContent = document.getElementById('dashboardContent');
    if (!dashboardContent || dashboardContent.style.display === 'none') {
        console.log('Not initializing charts - dashboard not visible');
        return;
    }

    console.log('Starting dashboard charts initialization');
    await cleanupCharts();

    try {
        // Fetch initial data
        const data = await fetchDashboardData();
        
        // Update stats
        updateDashboardStats(data);

        // Configure and initialize charts
        const profitConfig = {
            series: [
                { 
                    name: "Sales",
                    data: data.sales_expenses.sales,
                    color: '#49BEFF'
                },
                { 
                    name: "Expenses",
                    data: data.sales_expenses.expenses,
                    color: '#EA4646'
                }
            ],
            chart: {
                id: 'profit-chart-1',
                type: "bar",
                height: 345,
                toolbar: { 
                    show: true,
                    tools: {
                        download: true,
                        selection: false,
                        zoom: true,
                        zoomin: true,
                        zoomout: true,
                        pan: false,
                        reset: true
                    }
                }
            },
            plotOptions: {
                bar: {
                    horizontal: false,
                    columnWidth: '45%',
                    endingShape: 'rounded'
                },
            },
            dataLabels: { enabled: false },
            stroke: { show: true, width: 2, colors: ['transparent'] },
            xaxis: {
                categories: data.sales_expenses.dates,
            },
            yaxis: {
                title: { text: '$ (thousands)' }
            },
            tooltip: {
                y: {
                    formatter: function(val) {
                        return "$ " + val + " thousands"
                    }
                }
            }
        };

        const breakupConfig = {
            series: data.revenue_breakup.map(item => item.total),
            labels: data.revenue_breakup.map(item => item.product__category),
            chart: {
                id: 'breakup-chart',
                type: 'donut',
                height: 380
            },
            plotOptions: {
                pie: {
                    donut: {
                        size: '75%',
                        labels: {
                            show: true,
                            total: {
                                show: true,
                                showAlways: true,
                                label: 'Total Revenue',
                                fontSize: '22px',
                                fontFamily: 'Helvetica, Arial, sans-serif',
                                fontWeight: 600,
                                color: '#373d3f',
                                formatter: function(w) {
                                    return "$ " + w.globals.seriesTotals.reduce((a, b) => a + b, 0)
                                }
                            }
                        }
                    }
                }
            }
        };

        const earningConfig = {
            series: [{
                name: "Daily Earnings",
                data: data.weekly_earnings.map(day => day.total),
                color: '#49BEFF'
            }],
            chart: {
                id: 'earning-chart',
                type: 'line',
                height: 290,
                zoom: { enabled: false }
            },
            stroke: {
                curve: "smooth",
                width: 2,
            },
            xaxis: {
                categories: data.weekly_earnings.map(day => 
                    new Date(day.day).toLocaleDateString('en-US', { weekday: 'short' })
                )
            },
            tooltip: {
                y: {
                    formatter: function(val) {
                        return "$ " + val
                    }
                }
            }
        };

        // Initialize charts
        console.log('Initializing charts with real data...');
        const [profit, breakup, earning] = await Promise.all([
            initializeChart("profit-chart", profitConfig),
            initializeChart("breakup", breakupConfig),
            initializeChart("earning", earningConfig)
        ]);

        // Store chart instances
        dashboardCharts = { profit, breakup, earning };

        // Start periodic updates
        startPeriodicUpdates();

    } catch (error) {
        console.error('Error initializing dashboard charts:', error);
        await cleanupCharts();
    }
}

// Function to cleanup charts
async function cleanupCharts() {
    try {
        console.log('Starting chart cleanup...');
        for (const [chartName, chart] of Object.entries(dashboardCharts)) {
            if (chart) {
                try {
                    await chart.destroy();
                    console.log(`${chartName} chart destroyed successfully`);
                } catch (err) {
                    console.warn(`Error destroying ${chartName} chart:`, err);
                }
            }
        }
        dashboardCharts = { profit: null, breakup: null, earning: null };
        console.log('Dashboard charts cleaned up successfully');
    } catch (error) {
        console.error('Error in chart cleanup process:', error);
    }
}

// Periodic updates
let updateInterval;

function startPeriodicUpdates() {
    // Clear any existing interval
    if (updateInterval) clearInterval(updateInterval);
    
    // Update every 5 minutes
    updateInterval = setInterval(async () => {
        try {
            const data = await fetchDashboardData();
            
            // Update stats
            updateDashboardStats(data);
            
            // Update charts
            if (dashboardCharts.profit) {
                updateChartData(dashboardCharts.profit, {
                    series: [
                        { name: "Sales", data: data.sales_expenses.sales },
                        { name: "Expenses", data: data.sales_expenses.expenses }
                    ],
                    labels: data.sales_expenses.dates
                });
            }
            
            if (dashboardCharts.breakup) {
                updateChartData(dashboardCharts.breakup, {
                    series: data.revenue_breakup.map(item => item.total),
                    labels: data.revenue_breakup.map(item => item.product__category)
                });
            }
            
            if (dashboardCharts.earning) {
                updateChartData(dashboardCharts.earning, {
                    series: [{
                        name: "Daily Earnings",
                        data: data.weekly_earnings.map(day => day.total)
                    }],
                    labels: data.weekly_earnings.map(day => 
                        new Date(day.day).toLocaleDateString('en-US', { weekday: 'short' })
                    )
                });
            }
            
            console.log('Dashboard data updated successfully');
        } catch (error) {
            console.error('Error updating dashboard:', error);
        }
    }, 5 * 60 * 1000); // 5 minutes
}

function stopPeriodicUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
}

// Make functions globally available
window.initializeDashboardCharts = initializeDashboardCharts;
window.destroyDashboardCharts = async function() {
    stopPeriodicUpdates();
    await cleanupCharts();
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    const tryInitializeCharts = () => {
        const dashboardContent = document.getElementById('dashboardContent');
        if (dashboardContent) {
            if (dashboardContent.style.display !== 'none') {
                console.log('Dashboard content found, initializing charts...');
                initializeDashboardCharts().catch(err => {
                    console.error('Failed to initialize dashboard charts:', err);
                });
            } else {
                console.log('Dashboard content hidden, skipping chart initialization');
            }
        } else {
            console.log('Dashboard content not found yet, retrying...');
            setTimeout(tryInitializeCharts, 100);
        }
    };

    // Add resize handler
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            if (document.getElementById('dashboardContent')?.style.display !== 'none') {
                console.log('Window resized, reinitializing charts...');
                initializeDashboardCharts();
            }
        }, 250);
    });

    // Start initialization
    setTimeout(tryInitializeCharts, 500);
});