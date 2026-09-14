// Dashboard Chart.js & AJAX Handlers

let timelineChart = null;
let severityChart = null;
let attackChart = null;

document.addEventListener('DOMContentLoaded', () => {
  initCharts();
  setupEventHandlers();
});

function initCharts() {
  fetch('/api/chart-data')
    .then(res => res.json())
    .then(data => {
      renderTimelineChart(data.timeline);
      renderSeverityChart(data.severity);
      renderAttackChart(data.attack_types);
    })
    .catch(err => console.error("Chart data fetch error:", err));
}

function renderTimelineChart(timelineData) {
  const ctx = document.getElementById('timelineChart');
  if (!ctx) return;

  if (timelineChart) timelineChart.destroy();

  timelineChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: timelineData.labels,
      datasets: [
        {
          label: 'Successful Logins',
          data: timelineData.success,
          borderColor: '#00e676',
          backgroundColor: 'rgba(0, 230, 118, 0.1)',
          fill: true,
          tension: 0.3
        },
        {
          label: 'Failed Logins',
          data: timelineData.failed,
          borderColor: '#ff1744',
          backgroundColor: 'rgba(255, 23, 68, 0.1)',
          fill: true,
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#94a3b8' } }
      },
      scales: {
        x: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293c' } },
        y: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293c' } }
      }
    }
  });
}

function renderSeverityChart(sevData) {
  const ctx = document.getElementById('severityChart');
  if (!ctx) return;

  if (severityChart) severityChart.destroy();

  severityChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Low', 'Medium', 'High', 'Critical'],
      datasets: [{
        data: [sevData.Low, sevData.Medium, sevData.High, sevData.Critical],
        backgroundColor: ['#00e5ff', '#ffc400', '#ff9100', '#ff1744'],
        borderWidth: 1,
        borderColor: '#121827'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { color: '#94a3b8' } }
      }
    }
  });
}

function renderAttackChart(attackData) {
  const ctx = document.getElementById('attackChart');
  if (!ctx) return;

  if (attackChart) attackChart.destroy();

  const labels = Object.keys(attackData);
  const counts = Object.values(attackData);

  attackChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Alert Count',
        data: counts,
        backgroundColor: '#3b82f6',
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
        y: { ticks: { color: '#94a3b8' }, grid: { color: '#1e293c' } }
      }
    }
  });
}

function setupEventHandlers() {
  const btnSample = document.getElementById('btnLoadSample');
  if (btnSample) {
    btnSample.addEventListener('click', () => {
      btnSample.disabled = true;
      btnSample.innerHTML = `<i class="bi bi-hourglass-split"></i> Ingesting...`;
      fetch('/api/load-sample-data', { method: 'POST' })
        .then(res => res.json())
        .then(res => {
          alert(res.message || "Sample logs ingested!");
          window.location.reload();
        })
        .catch(err => {
          alert("Failed to load sample logs: " + err);
          btnSample.disabled = false;
        });
    });
  }

  const btnClear = document.getElementById('btnClearData');
  if (btnClear) {
    btnClear.addEventListener('click', () => {
      if (confirm("Are you sure you want to clear all logs and alerts?")) {
        fetch('/api/clear-data', { method: 'POST' })
          .then(res => res.json())
          .then(res => {
            alert(res.message);
            window.location.reload();
          });
      }
    });
  }
}
