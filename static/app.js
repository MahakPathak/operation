// -------------------------------
// Base API URL
// -------------------------------
const BASE = "/api";

// -------------------------------
// UI HELPERS
// -------------------------------
function getLoaderHTML() {
    return `<div class="loader"></div>`;
}

function badge(text, color) {
    return `<span class="badge ${color}">${text}</span>`;
}

// -------------------------------
// DATA LOADING FUNCTIONS
// -------------------------------

// RULES
async function loadRules() {
    const container = document.getElementById("rules");
    container.innerHTML = getLoaderHTML();
    try {
        const res = await fetch(`${BASE}/rules`);
        const data = await res.json();
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
    } catch (error) {
        container.innerHTML = `<p class="error">Failed to load rule-based status.</p>`;
    }
}

// OPTIMIZATION
async function loadOptimization() {
    const container = document.getElementById("opt");
    container.innerHTML = getLoaderHTML();
    const k = document.getElementById("kOpt").value;
    try {
        const res = await fetch(`${BASE}/optimization?k=${k}`);
        const data = await res.json();
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
    } catch (error) {
        container.innerHTML = `<p class="error">Failed to load optimization data.</p>`;
    }
}

// PREDICTIVE
async function loadPredictive() {
    const container = document.getElementById("pred");
    container.innerHTML = getLoaderHTML();
    try {
        const res = await fetch(`${BASE}/predictive`);
        const data = await res.json();
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
    } catch (error) {
        container.innerHTML = `<p class="error">Failed to load predictive maintenance data.</p>`;
    }
}

// WHAT-IF SIMULATOR
async function runWhatIf() {
    const container = document.getElementById("whatif");
    container.innerHTML = getLoaderHTML();
    const train = document.getElementById("wf_k").value;
    const bw = document.getElementById("wf_brand").value;
    const sw = document.getElementById("wf_stab").value;
    try {
        const res = await fetch(
            `${BASE}/whatif?k=${train}&branding_weight=${bw}&stabling_weight=${sw}`, {
                method: "POST"
            }
        );
        const data = await res.json();
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
    } catch (error) {
        container.innerHTML = `<p class="error">Failed to run what-if simulation.</p>`;
    }
}

// -------------------------------
// INITIALIZATION
// -------------------------------
async function loadAll() {
    loadRules();
    loadOptimization();
    loadPredictive();
    // Clear the what-if results on a full refresh
    document.getElementById("whatif").innerHTML = '';
}

// Theme Toggle Logic
function setupThemeToggle() {
    const toggle = document.getElementById('theme-toggle');
    const body = document.body;
    
    // Check for saved theme in localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        body.classList.add('dark-mode');
        toggle.checked = true;
    }

    toggle.addEventListener('change', () => {
        if (toggle.checked) {
            body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
        } else {
            body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
        }
    });
}


// Load everything when the page is ready
document.addEventListener('DOMContentLoaded', () => {
    setupThemeToggle();
    loadAll();
});