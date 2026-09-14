// Phishing URL Detector Frontend Logic

document.addEventListener('DOMContentLoaded', () => {
  setupPredictForm();
});

function setupPredictForm() {
  const form = document.getElementById('urlPredictForm');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const inputUrl = document.getElementById('inputUrl').value.trim();
    if (!inputUrl) return;

    const btnSubmit = document.getElementById('btnSubmitScan');
    const resultContainer = document.getElementById('resultContainer');
    
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = `<i class="bi bi-cpu-fill spin"></i> Extracting Features & Predicting...`;

    fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: inputUrl })
    })
    .then(res => res.json())
    .then(data => {
      btnSubmit.disabled = false;
      btnSubmit.innerHTML = `<i class="bi bi-shield-check"></i> Analyze & Predict URL Risk`;

      if (data.error) {
        resultContainer.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
      } else {
        renderPredictionResult(data);
      }
    })
    .catch(err => {
      btnSubmit.disabled = false;
      btnSubmit.innerHTML = `<i class="bi bi-shield-check"></i> Analyze & Predict URL Risk`;
      resultContainer.innerHTML = `<div class="alert alert-danger">Network Error: ${err}</div>`;
    });
  });
}

function renderPredictionResult(data) {
  const resultContainer = document.getElementById('resultContainer');
  const isPhishing = data.is_phishing;
  const boxClass = isPhishing ? 'result-box-phishing' : 'result-box-legit';
  const badgeClass = isPhishing ? 'badge-phishing' : 'badge-legit';
  const icon = isPhishing ? 'bi-shield-slash-fill text-danger' : 'bi-shield-check-fill text-success';

  let featRows = '';
  for (const [key, val] of Object.entries(data.features)) {
    featRows += `
      <div class="col-md-3 col-6 mb-2">
        <div class="p-2 bg-dark rounded border border-secondary text-center">
          <small class="text-muted d-block fs-8 font-monospace">${key}</small>
          <strong class="text-light fs-6">${val}</strong>
        </div>
      </div>
    `;
  }

  let expItems = '';
  data.explanations.forEach(exp => {
    expItems += `<li class="mb-1">${exp}</li>`;
  });

  resultContainer.innerHTML = `
    <div class="${boxClass} mb-4">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="d-flex align-items-center gap-3">
          <i class="bi ${icon} fs-1"></i>
          <div>
            <h3 class="m-0 text-light">${data.prediction}</h3>
            <div class="text-muted fs-7 font-monospace word-break-all">${data.url}</div>
          </div>
        </div>
        <div class="text-end">
          <span class="${badgeClass} fs-6">${data.prediction}</span>
          <div class="mt-2 text-muted fs-7">Risk Score: <strong class="text-light">${data.risk_score} / 100</strong></div>
        </div>
      </div>

      <div class="mb-3">
        <label class="form-label text-muted fs-7 me-2">Phishing Probability Confidence:</label>
        <strong class="text-light fs-6">${data.confidence_percent}%</strong>
        <div class="progress mt-1" style="height: 10px; background-color: #121212;">
          <div class="progress-bar ${isPhishing ? 'bg-danger' : 'bg-success'}" style="width: ${data.confidence_percent}%;"></div>
        </div>
      </div>

      <div class="mb-3">
        <strong class="text-light fs-7 d-block mb-1"><i class="bi bi-info-circle text-info"></i> Model Rationale & Key Feature Flags:</strong>
        <ul class="text-muted fs-7 ps-3 mb-0">
          ${expItems}
        </ul>
      </div>

      <div class="p-2 bg-dark rounded border border-secondary text-muted fs-8">
        <i class="bi bi-shield-exclamation text-warning me-1"></i> <strong>Disclaimer:</strong> ${data.disclaimer}
      </div>
    </div>

    <!-- Extracted Feature Vector Card -->
    <div class="soc-table-card">
      <div class="card-header-title">
        <span><i class="bi bi-cpu-fill text-info"></i> Extracted URL Feature Vector (12 Indicators)</span>
      </div>
      <div class="row g-2">
        ${featRows}
      </div>
    </div>
  `;

  resultContainer.scrollIntoView({ behavior: 'smooth' });
}
