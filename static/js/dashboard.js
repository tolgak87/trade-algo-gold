// Gold Trading Bot Dashboard - Real-time WebSocket Client

// Initialize Socket.IO connection
const socket = io();

// Chart.js instance
let priceChart = null;

// Connection status
socket.on('connect', () => {
    console.log('✅ Connected to dashboard server');
    updateConnectionStatus(true);
    socket.emit('request_state');
});

socket.on('disconnect', () => {
    console.log('❌ Disconnected from dashboard server');
    updateConnectionStatus(false);
});

// Update connection status badge
function updateConnectionStatus(connected) {
    const badge = document.getElementById('connection-status');
    if (connected) {
        badge.className = 'badge bg-success me-2';
        badge.innerHTML = '<i class="bi bi-wifi"></i> Connected';
    } else {
        badge.className = 'badge bg-danger me-2';
        badge.innerHTML = '<i class="bi bi-wifi-off"></i> Disconnected';
    }
}

// Update current time
function updateTime() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleTimeString();
}
setInterval(updateTime, 1000);
updateTime();

// ===== WebSocket Event Handlers =====

// Full state update
socket.on('state_update', (state) => {
    console.log('📊 State update received', state);
    
    if (state.bot_status) updateBotStatus(state.bot_status);
    if (state.account) updateAccountInfo(state.account);
    if (state.position !== undefined) updatePosition(state.position);
    if (state.sar_data) updateSARData(state.sar_data);
    if (state.signal) updateSignal(state.signal);
    if (state.last_trades) updateTradeHistory(state.last_trades);
    if (state.price_history) initPriceChart(state.price_history);
});

// Individual updates
socket.on('status_update', (data) => {
    updateBotStatus(data.status);
});

socket.on('account_update', (data) => {
    updateAccountInfo(data);
});

socket.on('position_update', (data) => {
    updatePosition(data);
});

socket.on('sar_update', (data) => {
    updateSARData(data);
});

socket.on('signal_update', (data) => {
    updateSignal(data);
});

socket.on('trade_added', (data) => {
    addTradeToHistory(data);
    showNotification(`Trade closed: ${data.type} | P/L: $${data.profit.toFixed(2)}`, 
                     data.profit >= 0 ? 'success' : 'danger');
});

socket.on('price_update', (data) => {
    addPricePoint(data);
});

socket.on('notification', (data) => {
    showNotification(data.message, data.type);
});

// ===== Update Functions =====

function updateBotStatus(status) {
    const banner = document.getElementById('bot-status-banner');
    const text = document.getElementById('bot-status-text');
    text.textContent = status;
    
    // Change banner color based on status
    if (status.toLowerCase().includes('position open') || status.toLowerCase().includes('monitoring')) {
        banner.className = 'alert alert-success d-flex align-items-center';
    } else if (status.toLowerCase().includes('waiting')) {
        banner.className = 'alert alert-info d-flex align-items-center';
    } else if (status.toLowerCase().includes('error')) {
        banner.className = 'alert alert-danger d-flex align-items-center';
    } else {
        banner.className = 'alert alert-warning d-flex align-items-center';
    }
}

function updateAccountInfo(account) {
    document.getElementById('account-balance').textContent = formatMoney(account.balance);
    document.getElementById('account-equity').textContent = formatMoney(account.equity);
    document.getElementById('account-free-margin').textContent = formatMoney(account.free_margin);
    
    const profitEl = document.getElementById('account-profit');
    profitEl.textContent = formatMoney(account.profit);
    profitEl.className = getProfitClass(account.profit);
}

function updatePosition(position) {
    const noPositionMsg = document.getElementById('no-position-msg');
    const positionDetails = document.getElementById('position-details');
    
    if (!position) {
        noPositionMsg.style.display = 'block';
        positionDetails.style.display = 'none';
        return;
    }
    
    noPositionMsg.style.display = 'none';
    positionDetails.style.display = 'block';
    
    // Update position type with badge
    const typeEl = document.getElementById('position-type');
    typeEl.innerHTML = `<span class="badge ${position.type === 'BUY' ? 'badge-buy' : 'badge-sell'}">${position.type}</span>`;
    
    document.getElementById('position-ticket').textContent = position.ticket || '--';
    document.getElementById('position-entry').textContent = formatPrice(position.entry_price);
    document.getElementById('position-current').textContent = formatPrice(position.current_price);
    document.getElementById('position-sl').textContent = formatPrice(position.stop_loss);
    document.getElementById('position-tp').textContent = formatPrice(position.take_profit);
    document.getElementById('position-duration').textContent = position.duration || '0:00:00';
    
    const profitEl = document.getElementById('position-profit');
    profitEl.textContent = formatMoney(position.profit);
    profitEl.className = getProfitClass(position.profit);
}

function updateSARData(sar) {
    document.getElementById('sar-value').textContent = formatPrice(sar.sar_value);
    
    const trendEl = document.getElementById('sar-trend');
    trendEl.textContent = sar.trend || '--';
    if (sar.trend === 'UPTREND') {
        trendEl.className = 'text-success trend-up';
    } else if (sar.trend === 'DOWNTREND') {
        trendEl.className = 'text-danger trend-down';
    } else {
        trendEl.className = 'text-light';
    }
    
    document.getElementById('sar-distance').textContent = sar.distance ? sar.distance.toFixed(2) : '--';
}

function updateSignal(signal) {
    const typeEl = document.getElementById('signal-type');
    const reasonEl = document.getElementById('signal-reason');
    const timeEl = document.getElementById('signal-time');
    
    typeEl.textContent = signal.type || 'HOLD';
    reasonEl.textContent = signal.reason || 'Waiting for signal...';
    
    if (signal.timestamp) {
        const time = new Date(signal.timestamp);
        timeEl.textContent = time.toLocaleTimeString();
    }
    
    // Update styling based on signal type
    const signalDisplay = typeEl.parentElement;
    signalDisplay.classList.remove('signal-buy', 'signal-sell', 'signal-hold');
    
    if (signal.type === 'BUY') {
        signalDisplay.classList.add('signal-buy');
        typeEl.className = 'display-4 text-success';
    } else if (signal.type === 'SELL') {
        signalDisplay.classList.add('signal-sell');
        typeEl.className = 'display-4 text-danger';
    } else {
        signalDisplay.classList.add('signal-hold');
        typeEl.className = 'display-4 text-muted';
    }
}

function updateTradeHistory(trades) {
    const tbody = document.getElementById('trade-history-body');
    
    if (!trades || trades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">No trades yet</td></tr>';
        return;
    }
    
    tbody.innerHTML = trades.map(trade => {
        const profitClass = getProfitClass(trade.profit);
        const typeClass = trade.type === 'BUY' ? 'badge-buy' : 'badge-sell';
        const time = new Date(trade.timestamp);
        
        return `
            <tr>
                <td>${trade.ticket || '--'}</td>
                <td><span class="badge ${typeClass}">${trade.type}</span></td>
                <td>${formatPrice(trade.entry_price)}</td>
                <td>${formatPrice(trade.close_price)}</td>
                <td>${trade.volume ? trade.volume.toFixed(2) : '--'}</td>
                <td class="${profitClass}">${formatMoney(trade.profit)}</td>
                <td>${trade.duration || '--'}</td>
                <td><small>${trade.close_reason || '--'}</small></td>
                <td><small>${time.toLocaleTimeString()}</small></td>
            </tr>
        `;
    }).join('');
}

function addTradeToHistory(trade) {
    // Request full state update to refresh trade history
    socket.emit('request_state');
}

// ===== Chart Functions =====

function initPriceChart(priceHistory) {
    const ctx = document.getElementById('price-chart');
    
    if (!ctx) return;
    
    const labels = priceHistory.map(p => {
        const time = new Date(p.timestamp);
        return time.toLocaleTimeString();
    });
    
    const priceData = priceHistory.map(p => p.price);
    const sarData = priceHistory.map(p => p.sar);
    
    if (priceChart) {
        priceChart.destroy();
    }
    
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'XAUUSD Price',
                    data: priceData,
                    borderColor: '#00aaff',
                    backgroundColor: 'rgba(0, 170, 255, 0.1)',
                    borderWidth: 2,
                    tension: 0.1,
                    pointRadius: 0
                },
                {
                    label: 'SAR Value',
                    data: sarData,
                    borderColor: '#ffaa00',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    tension: 0.1,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#fff'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff'
                }
            },
            scales: {
                x: {
                    ticks: { color: '#888' },
                    grid: { color: '#333' }
                },
                y: {
                    ticks: { color: '#888' },
                    grid: { color: '#333' }
                }
            }
        }
    });
}

function addPricePoint(point) {
    if (!priceChart) return;
    
    const time = new Date(point.timestamp);
    
    // Add new data point
    priceChart.data.labels.push(time.toLocaleTimeString());
    priceChart.data.datasets[0].data.push(point.price);
    priceChart.data.datasets[1].data.push(point.sar);
    
    // Keep only last 100 points
    if (priceChart.data.labels.length > 100) {
        priceChart.data.labels.shift();
        priceChart.data.datasets[0].data.shift();
        priceChart.data.datasets[1].data.shift();
    }
    
    priceChart.update('none'); // Update without animation for performance
}

// ===== Notification Toast =====

function showNotification(message, type = 'info') {
    const toast = document.getElementById('notification-toast');
    const toastBody = document.getElementById('toast-body');
    const toastTime = document.getElementById('toast-time');
    
    toastBody.textContent = message;
    toastTime.textContent = new Date().toLocaleTimeString();
    
    // Set color based on type
    const toastHeader = toast.querySelector('.toast-header');
    toastHeader.className = `toast-header bg-${type} text-${type === 'warning' ? 'dark' : 'white'}`;
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// ===== Utility Functions =====

function formatMoney(value) {
    if (value === null || value === undefined) return '$0.00';
    return '$' + Number(value).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function formatPrice(value) {
    if (value === null || value === undefined) return '--';
    return Number(value).toFixed(2);
}

function getProfitClass(profit) {
    if (profit > 0) return 'profit-positive';
    if (profit < 0) return 'profit-negative';
    return 'profit-zero';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Dashboard initialized');
    updateTime();
});
