let scenariosData = {};

document.addEventListener('DOMContentLoaded', () => {
    fetchStatus();
    fetchScenarios();
});

function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');
}

async function fetchStatus() {
    const res = await fetch('/api/status');
    const data = await res.json();
    
    document.getElementById('status-adk').textContent = `Google ADK: ${data.adk}`;
    document.getElementById('status-adk').className = `status-box ${data.adk.includes('Full') ? 'active' : 'warning'}`;
    
    document.getElementById('status-qdrant').textContent = `Qdrant: ${data.qdrant}`;
    document.getElementById('status-lyzr').textContent = `Lyzr: ${data.lyzr}`;
}

async function fetchScenarios() {
    const res = await fetch('/api/scenarios');
    scenariosData = await res.json();
    const selector = document.getElementById('scenario-selector');
    
    for (const [key, val] of Object.entries(scenariosData)) {
        const opt = document.createElement('option');
        opt.value = key;
        opt.textContent = val.name;
        selector.appendChild(opt);
    }
}

function loadScenario() {
    const key = document.getElementById('scenario-selector').value;
    if (key === 'custom') return;
    
    const data = scenariosData[key];
    document.getElementById('sens-elec').value = data.electrical_voltage;
    document.getElementById('sens-hyd').value = data.hydraulic_pressure;
    document.getElementById('sens-pneu').value = data.pneumatic_pressure;
    document.getElementById('sens-ram').value = data.ram_position;
    document.getElementById('sens-block').checked = data.mechanical_block_installed;
    document.getElementById('sens-breaker').checked = data.breaker_lock_verified;
    document.getElementById('sens-valve').checked = data.hydraulic_isolation_valve_verified;
    document.getElementById('sens-try').checked = data.try_start_completed;
    document.getElementById('sens-movement').checked = data.movement_detected;
    document.getElementById('sens-sup').checked = data.supervisor_approval;
    document.getElementById('sens-series').value = (data.hydraulic_pressure_series || []).join(', ');
}

function applyCorrectiveActions() {
    document.getElementById('scenario-selector').value = 'custom';
    document.getElementById('sens-elec').value = 0;
    document.getElementById('sens-hyd').value = 0.5;
    document.getElementById('sens-pneu').value = 0;
    document.getElementById('sens-ram').value = 'Raised';
    document.getElementById('sens-block').checked = true;
    document.getElementById('sens-breaker').checked = true;
    document.getElementById('sens-valve').checked = true;
    document.getElementById('sens-try').checked = true;
    document.getElementById('sens-movement').checked = false;
    document.getElementById('sens-sup').checked = false;
    document.getElementById('sens-series').value = "42, 31, 20, 11, 5, 1.8, 0.8, 0.5";
}

async function runAssessment() {
    document.getElementById('assessment-result').innerHTML = "Analyzing...";
    
    const payload = {
        request: {
            machine: document.getElementById('req-machine').value,
            component: document.getElementById('req-component').value,
            maintenance_task: document.getElementById('req-task').value,
            worker_name: document.getElementById('req-worker').value,
            worker_role: document.getElementById('req-role').value
        },
        sensors: {
            electrical_voltage: parseFloat(document.getElementById('sens-elec').value),
            hydraulic_pressure: parseFloat(document.getElementById('sens-hyd').value),
            pneumatic_pressure: parseFloat(document.getElementById('sens-pneu').value),
            ram_position: document.getElementById('sens-ram').value,
            mechanical_block_installed: document.getElementById('sens-block').checked,
            breaker_lock_verified: document.getElementById('sens-breaker').checked,
            hydraulic_isolation_valve_verified: document.getElementById('sens-valve').checked,
            try_start_completed: document.getElementById('sens-try').checked,
            movement_detected: document.getElementById('sens-movement').checked,
            supervisor_approval: document.getElementById('sens-sup').checked,
            hydraulic_pressure_series: document.getElementById('sens-series').value.split(',').map(n => parseFloat(n.trim())).filter(n => !isNaN(n))
        }
    };
    
    // Assess API
    const res = await fetch('/api/assess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    const data = await res.json();
    
    // Result banner
    const resultDiv = document.getElementById('assessment-result');
    if (data.verdict === 'RED') {
        resultDiv.innerHTML = `<div class="alert red">RED — MAINTENANCE BLOCKED</div>`;
    } else if (data.verdict === 'AMBER') {
        resultDiv.innerHTML = `<div class="alert amber">AMBER — MISSING EVIDENCE OR SENSOR ISSUES</div>`;
    } else {
        resultDiv.innerHTML = `<div class="alert green">GREEN — READY FOR AUTHORIZED HUMAN REVIEW ${!payload.sensors.supervisor_approval ? '<br><small>Supervisor authorization pending.</small>' : ''}</div>`;
    }
    
    // Populate Trace
    const tbody = document.querySelector('#trace-table tbody');
    tbody.innerHTML = '';
    data.report.agent_trace.forEach(t => {
        tbody.innerHTML += `
            <tr>
                <td>${t.order}</td>
                <td>${t.agent}</td>
                <td>${t.status}</td>
                <td>${t.duration.toFixed(3)}</td>
                <td>${t.input_summary}</td>
                <td>${t.output_summary}</td>
            </tr>
        `;
    });
    
    // Populate Memory
    const memDiv = document.getElementById('memory-results');
    memDiv.innerHTML = '<h4>Retrieved Near-Misses</h4>';
    data.report.near_miss_references.forEach(m => {
        memDiv.innerHTML += `
            <div style="margin-bottom:1rem; padding:1rem; background:var(--bg-dark); border-radius:6px; border: 1px solid var(--border);">
                <strong>${m.title}</strong> (Score: ${m.similarity_score.toFixed(4)})<br>
                ${m.content}
            </div>
        `;
    });
    
    // Populate Report
    const repDiv = document.getElementById('report-content');
    const r = data.report.assessment_result;
    repDiv.innerHTML = `
        <h3 style="color: ${data.verdict === 'RED' ? 'var(--red)' : 'var(--green)'}">Verdict: ${data.verdict}</h3>
        <p><strong>Blocking Hazards:</strong></p>
        <ul>${r.blocking_hazards.map(h => `<li>🚫 ${h}</li>`).join('')}</ul>
        <p><strong>Completed Controls:</strong></p>
        <ul>${r.completed_controls.map(c => `<li>✅ ${c}</li>`).join('')}</ul>
        <p><strong>Missing Evidence:</strong></p>
        <ul>${r.missing_evidence.map(e => `<li>⚠️ ${e}</li>`).join('')}</ul>
        <p><strong>Actions:</strong></p>
        <ul>${r.recommended_actions.map(a => `<li>🔧 ${a}</li>`).join('')}</ul>
        <hr>
        <p><em>${r.disclaimer}</em></p>
        <div class="mt-2">
            <button class="btn" onclick="window.location.href='/api/download/json'">Download JSON</button>
            <button class="btn" onclick="window.location.href='/api/download/md'">Download Markdown</button>
        </div>
    `;
    
    // Generate Graphviz
    const graphRes = await fetch('/api/graphviz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sensors: payload.sensors })
    });
    const graphData = await graphRes.json();
    document.getElementById('graph-container').innerHTML = graphData.svg;
}

async function seedMemory() {
    await fetch('/api/seed', { method: 'POST' });
    alert("Memory seeded successfully!");
    fetchStatus();
}
