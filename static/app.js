// -------------------------------
// Base API URL
// -------------------------------
const BASE = "/api";

// This will hold the chart instance so we can destroy it before creating a new one
let myStatsChart = null; 

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
        return data;
    } catch (error) {
        container.innerHTML = `<p class="error">Failed to load rule-based status.</p>`;
        return [];
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
        return data;
    } catch (error) {
        container.innerHTML = `<p class="error">Failed to load predictive maintenance data.</p>`;
        return [];
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

// FUNCTION TO UPDATE THE STATS
function updateStatCards(rulesData, predictiveData) {
    const statsContainer = document.getElementById('stats-container');
    
    const eligibleTrains = rulesData.filter(train => train.status === 'Eligible').length;
    const blockedTrains = rulesData.length - eligibleTrains;
    const needsMaintenance = predictiveData.filter(train => train.status === 'Warning' || train.status === 'Critical').length;
    const safeTrains = predictiveData.length - needsMaintenance;
    
    const statsHTML = `
        <div class="stat-box eligible">
            <div class="stat-box-content">
                <div class="stat-box-text">
                    <div class="title">Eligible Trains</div>
                    <div class="value">${eligibleTrains}</div>
                </div>
                <div class="stat-box-icon"><i class="fa-solid fa-check-to-slot"></i></div>
            </div>
        </div>
        <div class="stat-box blocked">
            <div class="stat-box-content">
                <div class="stat-box-text">
                    <div class="title">Blocked Trains</div>
                    <div class="value">${blockedTrains}</div>
                </div>
                <div class="stat-box-icon"><i class="fa-solid fa-xmark-circle"></i></div>
            </div>
        </div>
        <div class="stat-box maintenance">
            <div class="stat-box-content">
                <div class="stat-box-text">
                    <div class="title">Needs Maintenance</div>
                    <div class="value">${needsMaintenance}</div>
                </div>
                <div class="stat-box-icon"><i class="fa-solid fa-screwdriver-wrench"></i></div>
            </div>
        </div>
        <div class="stat-box safe">
            <div class="stat-box-content">
                <div class="stat-box-text">
                    <div class="title">Safe Trains</div>
                    <div class="value">${safeTrains}</div>
                </div>
                <div class="stat-box-icon"><i class="fa-solid fa-shield-halved"></i></div>
            </div>
        </div>
    `;

    statsContainer.innerHTML = statsHTML;
    
    renderStatsChart({ eligibleTrains, blockedTrains, needsMaintenance, safeTrains });
}

// RENDER THE CHART
function renderStatsChart(statsData) {
    const ctx = document.getElementById('stats-chart').getContext('2d');

    if (myStatsChart) {
        myStatsChart.destroy();
    }

    // CHANGED: The entire chart configuration is updated for a pie chart
    myStatsChart = new Chart(ctx, {
        type: 'pie', // CHANGED: from 'bar' to 'pie'
        data: {
            labels: ['Eligible', 'Blocked', 'Needs Maintenance', 'Safe'],
            datasets: [{
                label: 'Number of Trains',
                data: [
                    statsData.eligibleTrains, 
                    statsData.blockedTrains, 
                    statsData.needsMaintenance, 
                    statsData.safeTrains
                ],
                backgroundColor: [
                    'rgba(40, 167, 69, 0.8)',  // Green
                    'rgba(220, 53, 69, 0.8)',   // Red
                    'rgba(255, 193, 7, 0.8)',   // Yellow
                    'rgba(40, 167, 69, 0.5)'   // Lighter Green for Safe
                ],
                borderColor: [
                    'rgba(255, 255, 255, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true, // CHANGED: Show the legend
                    position: 'top', // Position legend at the top
                },
                title: {
                    display: true,
                    text: 'Overall Fleet Status Breakdown',
                    font: {
                        size: 16
                    }
                }
            }
            // REMOVED: The 'scales' option is not used for pie charts
        }
    });
}


// -------------------------------
// INITIALIZATION
// -------------------------------
async function loadAll() {
    loadOptimization();
    
    const rulesPromise = loadRules();
    const predictivePromise = loadPredictive();

    const [rulesData, predictiveData] = await Promise.all([rulesPromise, predictivePromise]);

    updateStatCards(rulesData, predictiveData);

    document.getElementById("whatif").innerHTML = '';
}

// Theme Toggle Logic
function setupThemeToggle() {
    const toggle = document.getElementById('theme-toggle');
    const body = document.body;
    
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