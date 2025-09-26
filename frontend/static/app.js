const LOCAL_API_PORT = 8000;

const BASE = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost"
  ? `http://127.0.0.1:${LOCAL_API_PORT}/api`
  : "https://your-app-name.onrender.com/api";


function badge(text, color) {
  return `<span class="badge ${color}">${text}</span>`;
}

// ---------- RULES ----------
async function loadRules() {
  const res = await fetch(`${BASE}/rules`);
  const data = await res.json();
  const container = document.getElementById("rules");

  let html = `<table><tr><th>ID</th><th>Status</th><th>Alerts</th></tr>`;
  data.forEach(row => {
    const color = row.status === "Eligible" ? "green" : "red";
    html += `
      <tr>
        <td>${row.id}</td>
        <td>${badge(row.status, color)}</td>
        <td>${row.alerts || "-"}</td>
      </tr>`;
  });
  html += `</table>`;

  container.innerHTML = html;
}

// ---------- OPTIMIZATION ----------
async function loadOptimization() {
  const k = document.getElementById("kOpt").value;
  const res = await fetch(`${BASE}/optimization?k=${k}`);
  const data = await res.json();
  const container = document.getElementById("opt");

  let html = `<table><tr><th>ID</th><th>Branding</th><th>Mileage</th><th>Score</th></tr>`;
  data.forEach(row => {
    html += `
      <tr>
        <td>${row.id}</td>
        <td>${row.branding}</td>
        <td>${row.mileage}</td>
        <td>${Math.round(row.score)}</td>
      </tr>`;
  });
  html += `</table>`;

  container.innerHTML = html;
}

// ---------- PREDICTIVE ----------
async function loadPredictive() {
  const res = await fetch(`${BASE}/predictive`);
  const data = await res.json();
  const container = document.getElementById("pred");

  let html = `<table><tr><th>ID</th><th>Route</th><th>Mileage</th><th>Predicted Days</th><th>Status</th></tr>`;
  data.forEach(row => {
    let color = "green";
    if (row.status === "Warning") color = "yellow";
    if (row.status === "Critical") color = "red";

    html += `
      <tr>
        <td>${row.id}</td>
        <td>${row.route}</td>
        <td>${row.mileage}</td>
        <td>${Math.round(row.predicted_days)}</td>
        <td>${badge(row.status, color)}</td>
      </tr>`;
  });
  html += `</table>`;

  container.innerHTML = html;
}



// ---------- WHAT-IF ----------
async function runWhatIf() {
  const train = document.getElementById("wf_k").value;
  const bw = document.getElementById("wf_brand").value;
  const sw = document.getElementById("wf_stab").value;

  const res = await fetch(
    `${BASE}/whatif?k=${train}&branding_weight=${bw}&stabling_weight=${sw}`,
    { method: "POST" }
  );
  const data = await res.json();
  const container = document.getElementById("whatif");

  let html = `<table><tr><th>ID</th><th>Branding</th><th>Mileage</th><th>Score</th></tr>`;
  data.forEach(row => {
    html += `
      <tr>
        <td>${row.id}</td>
        <td>${row.branding}</td>
        <td>${row.mileage}</td>
        <td>${Math.round(row.score)}</td>
      </tr>`;
  });
  html += `</table>`;

  container.innerHTML = html;
}

// ---------- LOAD ALL ----------
async function loadAll() {
  loadRules();
  loadOptimization();
  loadPredictive();
}
