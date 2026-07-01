/**
 * egbp.js — EGBP Calculator frontend logic
 */

let elements = [];
let engines = [];
let elId = 0;
let engineId = 0;
let lastEGBPResult = null;

document.addEventListener('DOMContentLoaded', () => {
    const addBtn = document.getElementById('addElement');
    const addEngineBtn = document.getElementById('addEngine');
    const form = document.getElementById('egbpForm');
    const downloadBtn = document.getElementById('downloadEGBPReport');

    if (addBtn) addBtn.addEventListener('click', () => addElement());
    if (addEngineBtn) addEngineBtn.addEventListener('click', () => addEngine());
    if (form) form.addEventListener('submit', handleEGBPCompute);
    if (downloadBtn) downloadBtn.addEventListener('click', downloadEGBPReport);

    // Initial source and element
    addEngine('ME');
    addElement('pipe');
});

function addEngine(type = 'ME') {
    const id = ++engineId;
    const preset = ENGINE_PRESETS[type] || { mass_flow: 0, temp_tc: 0, max_bp_pa: 3000, roughness: 'steel_welded' };
    engines.push({ 
        id, 
        type, 
        mass_flow: preset.mass_flow, 
        temp: preset.temp_tc,
        max_bp: preset.max_bp_pa || 3000,
        roughness: preset.roughness || 'steel_welded'
    });
    renderEngines();
    calculateSystemTotals();
}

function removeEngine(id) {
    engines = engines.filter(e => e.id !== id);
    renderEngines();
    calculateSystemTotals();
}

function updateEngineType(id, type) {
    const engine = engines.find(e => e.id === id);
    if (engine) {
        engine.type = type;
        const preset = ENGINE_PRESETS[type];
        if (preset) {
            engine.mass_flow = preset.mass_flow;
            engine.temp = preset.temp_tc;
            engine.max_bp = preset.max_bp_pa || 3000;
            engine.roughness = preset.roughness || 'steel_welded';
        }
        renderEngines();
        calculateSystemTotals();
    }
}

function updateEngineParam(id, field, value) {
    const engine = engines.find(e => e.id === id);
    if (engine) {
        engine[field] = field === 'roughness' ? value : (parseFloat(value) || 0);
        calculateSystemTotals();
    }
}

function renderEngines() {
    const body = document.getElementById('enginesBody');
    if (!body) return;
    
    body.innerHTML = '';
    engines.forEach((en, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${index + 1}</td>
            <td>
                <select class="type-select" onchange="updateEngineType(${en.id}, this.value)">
                    <option value="custom" ${en.type === 'custom' ? 'selected' : ''}>-- Custom Source --</option>
                    ${Object.entries(ENGINE_PRESETS).map(([key, p]) => `
                        <option value="${key}" ${en.type === key ? 'selected' : ''}>${p.label}</option>
                    `).join('')}
                </select>
            </td>
            <td>
                <div class="grid grid-4" style="gap: 0.5rem">
                    <div class="field-group">
                        <label style="font-size: 0.7rem; margin-bottom: 0.2rem">Mass Flow (kg/s)</label>
                        <input type="number" step="0.001" placeholder="Mass Flow" 
                            value="${en.mass_flow}" oninput="updateEngineParam(${en.id}, 'mass_flow', this.value)">
                    </div>
                    <div class="field-group">
                        <label style="font-size: 0.7rem; margin-bottom: 0.2rem">Temp (°C)</label>
                        <input type="number" step="0.1" placeholder="Temp" 
                            value="${en.temp}" oninput="updateEngineParam(${en.id}, 'temp', this.value)">
                    </div>
                    <div class="field-group">
                        <label style="font-size: 0.7rem; margin-bottom: 0.2rem">Max BP (Pa)</label>
                        <input type="number" step="1" placeholder="Max BP" 
                            value="${en.max_bp}" oninput="updateEngineParam(${en.id}, 'max_bp', this.value)">
                    </div>
                    <div class="field-group">
                        <label style="font-size: 0.7rem; margin-bottom: 0.2rem">Roughness</label>
                        <select onchange="updateEngineParam(${en.id}, 'roughness', this.value)">
                            ${Object.entries(ROUGHNESS_OPTIONS).map(([key, val]) => `
                                <option value="${key}" ${en.roughness === key ? 'selected' : ''}>
                                    ${key.replace('_', ' ').title()} (${val}mm)
                                </option>
                            `).join('')}
                        </select>
                    </div>
                </div>
            </td>
            <td>
                <button type="button" class="btn btn-outline" onclick="removeEngine(${en.id})" style="color: var(--danger); padding: 0.5rem">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        body.appendChild(tr);
    });
}

// Add String.prototype.title if it doesn't exist for roughness labels
if (!String.prototype.title) {
    String.prototype.title = function() {
        return this.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');
    };
}

function calculateSystemTotals() {
    let totalMass = 0;
    let weightedTempSum = 0;
    let minMaxBp = Infinity;
    let primaryRoughness = 'steel_welded';

    engines.forEach((en, i) => {
        totalMass += en.mass_flow;
        weightedTempSum += (en.mass_flow * en.temp);
        if (en.max_bp < minMaxBp) minMaxBp = en.max_bp;
        if (i === 0) primaryRoughness = en.roughness; // Default to first engine's roughness
    });

    const avgTemp = totalMass > 0 ? weightedTempSum / totalMass : 0;
    if (minMaxBp === Infinity) minMaxBp = 3000;

    document.getElementById('mass_flow_kgs').value = totalMass.toFixed(3);
    document.getElementById('temp_tc_c').value = avgTemp.toFixed(1);
    document.getElementById('max_bp_pa').value = minMaxBp;
    document.getElementById('roughness_key').value = primaryRoughness;
}

function addElement(type = 'pipe') {
    const id = ++elId;
    elements.push({ id, type });
    renderElements();
}

function removeElement(id) {
    elements = elements.filter(e => e.id !== id);
    renderElements();
}

function updateElementType(id, type) {
    const el = elements.find(e => e.id === id);
    if (el) {
        el.type = type;
        renderElements();
    }
}

function renderElements() {
    const body = document.getElementById('elementsBody');
    if (!body) return;
    
    body.innerHTML = '';
    elements.forEach((el, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${index + 1}</td>
            <td>
                <select class="type-select" onchange="updateElementType(${el.id}, this.value)">
                    <option value="pipe" ${el.type === 'pipe' ? 'selected' : ''}>Straight Pipe</option>
                    <option value="pipe_bend" ${el.type === 'pipe_bend' ? 'selected' : ''}>Pipe Bend</option>
                    <option value="diffuser" ${el.type === 'diffuser' ? 'selected' : ''}>Diffuser / Reduction</option>
                    <option value="wye_through" ${el.type === 'wye_through' ? 'selected' : ''}>Wye (through)</option>
                    <option value="wye_branch" ${el.type === 'wye_branch' ? 'selected' : ''}>Wye (branch)</option>
                    <option value="butterfly_valve" ${el.type === 'butterfly_valve' ? 'selected' : ''}>Butterfly Valve</option>
                    <option value="gate_valve" ${el.type === 'gate_valve' ? 'selected' : ''}>Gate Valve</option>
                    <option value="silencer" ${el.type === 'silencer' ? 'selected' : ''}>Silencer</option>
                    <option value="boiler" ${el.type === 'boiler' ? 'selected' : ''}>Boiler</option>
                    <option value="outlet" ${el.type === 'outlet' ? 'selected' : ''}>Outlet</option>
                    <option value="orifice" ${el.type === 'orifice' ? 'selected' : ''}>Orifice</option>
                    <option value="custom" ${el.type === 'custom' ? 'selected' : ''}>Custom ξ</option>
                </select>
            </td>
            <td>
                <div class="grid grid-2" id="inputs-${el.id}" style="gap: 0.5rem">
                    ${renderInputs(el)}
                </div>
            </td>
            <td>
                <button type="button" class="btn btn-outline" onclick="removeElement(${el.id})" style="color: var(--danger); padding: 0.5rem">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        body.appendChild(tr);
    });
}

function renderInputs(el) {
    switch (el.type) {
        case 'pipe':
            return `
                <input type="number" step="1" placeholder="Dia (mm)" class="el-dia" value="${el.dia || 1600}">
                <input type="number" step="1" placeholder="Length (mm)" class="el-len" value="${el.len || 1000}">
            `;
        case 'pipe_bend':
            return `
                <input type="number" step="1" placeholder="Dia (mm)" class="el-dia" value="${el.dia || 1600}">
                <div class="grid grid-2" style="gap: 0.5rem; width: 100%">
                    <input type="number" step="0.1" placeholder="R/d" class="el-rd" value="${el.rd || 1.5}">
                    <input type="number" step="1" placeholder="Angle (°)" class="el-angle" value="${el.angle || 90}">
                </div>
            `;
        case 'diffuser':
        case 'orifice':
            return `
                <input type="number" step="1" placeholder="Inlet (mm)" class="el-in" value="${el.in || 1600}">
                <input type="number" step="1" placeholder="Outlet (mm)" class="el-out" value="${el.out || 2410}">
            `;
        case 'custom':
            return `
                <input type="number" step="1" placeholder="Dia (mm)" class="el-dia" value="${el.dia || 1600}">
                <input type="number" step="0.001" placeholder="ξ value" class="el-xi" value="${el.xi || 1.0}">
            `;
        default:
            return `<input type="number" step="1" placeholder="Dia (mm)" class="el-dia" value="${el.dia || 1600}">`;
    }
}

async function handleEGBPCompute(e) {
    e.preventDefault();
    const resultsArea = document.getElementById('egbpResults');
    resultsArea.classList.add('hidden');

    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calculating...';

    const payload = {
        mass_flow_kgs: parseFloat(document.getElementById('mass_flow_kgs').value),
        temp_tc_c: parseFloat(document.getElementById('temp_tc_c').value),
        max_bp_pa: parseFloat(document.getElementById('max_bp_pa').value),
        roughness_key: document.getElementById('roughness_key').value,
        engines: engines.map(en => ({
            type: en.type,
            label: ENGINE_PRESETS[en.type]?.label || 'Custom Source',
            mass_flow: en.mass_flow,
            temp: en.temp,
            max_bp: en.max_bp,
            roughness: en.roughness
        })),
        elements: elements.map((el, i) => {
            const container = document.getElementById(`inputs-${el.id}`);
            return {
                element_type: el.type,
                diameter_mm: parseFloat(container.querySelector('.el-dia')?.value || 0),
                length_mm: parseFloat(container.querySelector('.el-len')?.value || 0),
                rd: parseFloat(container.querySelector('.el-rd')?.value || 1.5),
                angle_deg: parseFloat(container.querySelector('.el-angle')?.value || 90),
                inlet_a_mm: parseFloat(container.querySelector('.el-in')?.value || 0),
                outlet_b_mm: parseFloat(container.querySelector('.el-out')?.value || 0),
                xi_custom: parseFloat(container.querySelector('.el-xi')?.value || 1.0)
            };
        })
    };

    try {
        const res = await fetch('/calculate-egbp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        if (data.error) {
            alert(data.error);
            return;
        }

        lastEGBPResult = data;
        renderResults(data);
    } catch (err) {
        alert("Error connecting to server.");
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

function renderResults(d) {
    const resultsArea = document.getElementById('egbpResults');
    resultsArea.classList.remove('hidden');

    document.getElementById('totalPa').textContent = d.total_pressure_pa.toLocaleString();
    document.getElementById('totalMmwc').textContent = d.total_pressure_mmwc + ' mmWC';
    document.getElementById('limitPa').textContent = d.max_bp_pa.toLocaleString();
    
    const badge = document.getElementById('statusBadge');
    badge.textContent = d.status;
    badge.className = 'metric-value ' + (d.status === 'PASSED' ? 'badge-success' : d.status === 'BORDERLINE' ? 'badge-warning' : 'badge-danger');
    
    document.getElementById('marginText').textContent = d.margin_pct + '% margin';

    const tbody = document.querySelector('#resultsTable tbody');
    tbody.innerHTML = d.elements.map(el => `
        <tr>
            <td>${el.position}</td>
            <td><strong>${el.label}</strong></td>
            <td>${el.velocity.toFixed(2)}</td>
            <td>${el.xi.toFixed(4)}</td>
            <td>${el.pressure_loss_pa.toFixed(1)}</td>
            <td><small class="text-muted">${el.note}</small></td>
        </tr>
    `).join('');
    
    resultsArea.scrollIntoView({ behavior: 'smooth' });
}

async function downloadEGBPReport() {
    if (!lastEGBPResult) {
        alert("Please run a calculation first.");
        return;
    }

    const btn = document.getElementById('downloadEGBPReport');
    const originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';

    try {
        const res = await fetch('/api/egbp-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(lastEGBPResult)
        });

        if (res.ok) {
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `EGBP_Report_${new Date().getTime()}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            const err = await res.json();
            alert("Failed to generate report: " + (err.error || "Unknown error"));
        }
    } catch (err) {
        alert("Error generating report.");
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalHtml;
    }
}
