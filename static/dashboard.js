let statusChartInstance = null;
let failureChartInstance = null;
let typeChartInstance = null;
let wearChartInstance = null;

const COLORS = {
    chartBg: [
        'rgba(79, 195, 247, 0.85)',
        'rgba(239, 83, 80, 0.85)',
        'rgba(255, 167, 38, 0.85)',
        'rgba(171, 71, 188, 0.85)',
        'rgba(38, 166, 154, 0.85)',
        'rgba(236, 64, 122, 0.85)'
    ],
    chartBorder: ['#4fc3f7','#ef5350','#ffa726','#ab47bc','#26a69a','#ec407a']
};

document.addEventListener('DOMContentLoaded', loadDashboard);

function loadDashboard() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.style.display = 'flex';

    fetch('/api/dashboard-data')
        .then(res => res.json())
        .then(data => {
            updateKPIs(data);
            updateStats(data);
            renderStatusChart(data);
            renderFailureChart(data);
            renderTypeChart(data);
            renderWearChart(data);
            renderTable(data.sample_data);
            overlay.style.display = 'none';
        })
        .catch(err => {
            console.error('Dashboard load error:', err);
            overlay.innerHTML = '<p style="color:#ef5350;">Failed to load data. Make sure Flask is running.</p>';
        });
}

function animateValue(el, target, suffix = '') {
    let current = 0;
    const duration = 1000;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        el.textContent = Math.floor(current).toLocaleString() + suffix;
    }, 16);
}

function updateKPIs(data) {
    animateValue(document.getElementById('kpiTotal'), data.total);
    animateValue(document.getElementById('kpiWorking'), data.working);
    animateValue(document.getElementById('kpiFailed'), data.failed);
    document.getElementById('kpiRate').textContent = data.failure_rate + '%';
}

function updateStats(data) {
    document.getElementById('statAirTemp').textContent = data.avg_air_temp + ' K';
    document.getElementById('statProcessTemp').textContent = data.avg_process_temp + ' K';
    document.getElementById('statRPM').textContent = Math.floor(data.avg_rpm).toLocaleString();
    document.getElementById('statTorque').textContent = data.avg_torque + ' Nm';
    document.getElementById('statHighWear').textContent = data.high_wear_count.toLocaleString();
}

function renderStatusChart(data) {
    if (statusChartInstance) statusChartInstance.destroy();
    const ctx = document.getElementById('statusChart').getContext('2d');
    statusChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Working', 'Failed'],
            datasets: [{
                data: [data.working, data.failed],
                backgroundColor: ['rgba(76,175,80,0.85)', 'rgba(239,83,80,0.85)'],
                borderColor: ['#4caf50', '#ef5350'],
                borderWidth: 2, hoverOffset: 8
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false, cutout: '65%',
            plugins: { legend: { position: 'bottom', labels: { padding: 20, font: { size: 13 } } } }
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
                label: 'Count', data: data.failure_types.values,
                backgroundColor: COLORS.chartBg, borderColor: COLORS.chartBorder,
                borderWidth: 2, borderRadius: 6, borderSkipped: false
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.06)' } },
                x: { grid: { display: false }, ticks: { maxRotation: 45 } }
            }
        }
    });
}

function renderTypeChart(data) {
    if (typeChartInstance) typeChartInstance.destroy();
    const ctx = document.getElementById('typeChart').getContext('2d');
    typeChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.machine_types.labels,
            datasets: [{
                data: data.machine_types.values,
                backgroundColor: ['rgba(79,195,247,0.85)','rgba(255,167,38,0.85)','rgba(171,71,188,0.85)'],
                borderColor: ['#4fc3f7','#ffa726','#ab47bc'],
                borderWidth: 2, hoverOffset: 8
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false, cutout: '65%',
            plugins: { legend: { position: 'bottom', labels: { padding: 20, font: { size: 13 } } } }
        }
    });
}

function renderWearChart(data) {
    if (wearChartInstance) wearChartInstance.destroy();
    const ctx = document.getElementById('wearChart').getContext('2d');
    wearChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.tool_wear.labels,
            datasets: [{
                label: 'Machines', data: data.tool_wear.values,
                backgroundColor: 'rgba(79,195,247,0.7)', borderColor: '#4fc3f7',
                borderWidth: 2, borderRadius: 6, borderSkipped: false
            }]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.06)' } },
                x: { grid: { display: false } }
            }
        }
    });
}

function renderTable(rows) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';
    rows.forEach(row => {
        const statusBadge = row['Target'] === 1
            ? '<span class="badge badge-failed">Failed</span>'
            : '<span class="badge badge-working">Working</span>';
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row['UDI']}</td>
            <td>${row['Product ID']}</td>
            <td><span class="badge badge-type">${row['Type']}</span></td>
            <td>${row['Air temperature [K]']}</td>
            <td>${row['Process temperature [K]']}</td>
            <td>${row['Rotational speed [rpm]']}</td>
            <td>${row['Torque [Nm]']}</td>
            <td>${row['Tool wear [min]']}</td>
            <td>${statusBadge}</td>
            <td>${row['Failure Type']}</td>
        `;
        tbody.appendChild(tr);
    });
}
