let statusChartInstance = null;
let failureChartInstance = null;
let speedGaugeInstance = null;
let torqueGaugeInstance = null;

const THEME = {
    accent: '#0891b2',
    accentLight: '#22d3ee',
    primary: '#0f172a',
    muted: '#94a3b8',
    success: '#10b981',
    danger: '#ef4444',
    warning: '#f59e0b',
    grid: 'rgba(15, 23, 42, 0.04)',
    colors: ['#0891b2', '#0f172a', '#64748b', '#22d3ee', '#1e293b']
};

document.addEventListener('DOMContentLoaded', loadDashboard);

function loadDashboard() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.opacity = '1';
        overlay.style.display = 'flex';
    }

    fetch('/api/dashboard-data')
        .then(res => res.json())
        .then(data => {
            updateKPIs(data);
            renderStatusChart(data);
            renderFailureChart(data);
            renderSpeedGauge(data.avg_rpm);
            renderTorqueGauge(data.avg_torque);
            renderTable(data.sample_data);
            
            if (overlay) {
                overlay.style.opacity = '0';
                setTimeout(() => overlay.style.display = 'none', 500);
            }
            initReveals();
        })
        .catch(err => {
            console.error('Data Sync Error:', err);
            if (overlay) overlay.innerHTML = '<div style="color:red">SYNC FAILED: TIMEOUT</div>';
        });
}

function updateKPIs(data) {
    animateValue('kpiTotal', data.total);
    animateValue('kpiWorking', data.working);
    animateValue('kpiFailed', data.failed);
    const rateEl = document.getElementById('kpiRate');
    if (rateEl) rateEl.textContent = data.failure_rate + '%';
}

function animateValue(id, target) {
    const el = document.getElementById(id);
    if (!el) return;
    let current = 0;
    const duration = 2000;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        el.textContent = Math.floor(current).toLocaleString();
    }, 16);
}

function renderStatusChart(data) {
    if (statusChartInstance) statusChartInstance.destroy();
    const ctx = document.getElementById('statusChart').getContext('2d');
    statusChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['STABLE', 'FAULTED'],
            datasets: [{
                data: [data.working, data.failed],
                backgroundColor: [THEME.success, THEME.danger],
                hoverBackgroundColor: [THEME.success, THEME.danger],
                borderWidth: 0,
                weight: 1
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false, cutout: '85%',
            plugins: {
                legend: { position: 'bottom', labels: { usePointStyle: true, font: { family: "'Plus Jakarta Sans'", weight: '800', size: 12 }, padding: 30 } }
            }
        }
    });
}

function renderFailureChart(data) {
    if (failureChartInstance) failureChartInstance.destroy();
    const ctx = document.getElementById('failureChart').getContext('2d');
    
    failureChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.failure_types.labels,
            datasets: [{
                label: 'FAULT NODES',
                data: data.failure_types.values,
                backgroundColor: THEME.accent,
                borderRadius: 12,
                barThickness: 24
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: THEME.grid }, ticks: { font: { weight: '600' }, color: THEME.muted } },
                x: { grid: { display: false }, ticks: { font: { weight: '700' }, color: THEME.muted } }
            }
        }
    });
}

function renderSpeedGauge(val) {
    if (speedGaugeInstance) speedGaugeInstance.destroy();
    const ctx = document.getElementById('speedGauge').getContext('2d');
    document.getElementById('speedText').textContent = Math.round(val);
    
    speedGaugeInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [val, 3000 - val],
                backgroundColor: [THEME.primary, 'rgba(0,0,0,0.05)'],
                borderWidth: 0,
                circumference: 220,
                rotation: 250,
                borderRadius: 15
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false, cutout: '90%',
            plugins: { tooltip: { enabled: false }, legend: { display: false } },
            animation: { animateRotate: true, duration: 2500 }
        }
    });
}

function renderTorqueGauge(val) {
    if (torqueGaugeInstance) torqueGaugeInstance.destroy();
    const ctx = document.getElementById('torqueGauge').getContext('2d');
    document.getElementById('torqueText').textContent = val.toFixed(1);

    torqueGaugeInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [val, 80 - val],
                backgroundColor: [THEME.accent, 'rgba(0,0,0,0.05)'],
                borderWidth: 0,
                circumference: 220,
                rotation: 250,
                borderRadius: 15
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false, cutout: '90%',
            plugins: { tooltip: { enabled: false }, legend: { display: false } },
            animation: { animateRotate: true, duration: 2500 }
        }
    });
}

function renderTable(rows) {
    const tbody = document.getElementById('tableBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    
    rows.forEach(row => {
        const tr = document.createElement('tr');
        const statusBadge = row['Target'] === 1 ? 'badge-failed' : 'badge-working';
        const risk = (row['Risk'] || 'Safe').toUpperCase();
        
        tr.innerHTML = `
            <td style="font-family:'JetBrains Mono'; font-size:12px; font-weight:800;">#${row['UDI']}</td>
            <td><b>${row['Product ID']}</b></td>
            <td style="font-size:12px; font-weight:800; color:var(--accent);">${row['Type']}</td>
            <td>${row['Air temperature [K]']}K</td>
            <td style="font-family:'JetBrains Mono';">${Math.round(row['Rotational speed [rpm]'])}</td>
            <td style="font-family:'JetBrains Mono';">${row['Torque [Nm]']}</td>
            <td style="font-family:'JetBrains Mono';">${row['Tool wear [min]']}m</td>
            <td><span class="badge ${statusBadge}">${row['Target'] === 1 ? 'FAULT' : 'STABLE'}</span></td>
            <td><span style="font-size:11px; font-weight:800; opacity:0.6;">${risk}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function initReveals() {
    const reveals = document.querySelectorAll('.reveal');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) entry.target.classList.add('active');
        });
    }, { threshold: 0.1 });
    reveals.forEach(r => observer.observe(r));
}
