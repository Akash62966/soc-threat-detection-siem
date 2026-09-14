// Alerts Management JavaScript

function updateAlertStatus(alertId, newStatus) {
  fetch(`/api/alerts/${alertId}/status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: newStatus })
  })
  .then(res => res.json())
  .then(data => {
    if (data.message) {
      window.location.reload();
    } else {
      alert("Failed to update alert: " + (data.error || "Unknown error"));
    }
  })
  .catch(err => alert("Error updating alert status: " + err));
}
