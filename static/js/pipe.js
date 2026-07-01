// pipe.js - Pipe Wall Thickness Calculator frontend logic

let lastPipeResult = null;
let lastPipeInput = null;

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('pipeForm');
    if (form) {
        form.addEventListener('submit', handlePipeCalculate);
    }
    
    // Add event listener for download button
    document.addEventListener('click', (e) => {
        if (e.target.id === 'downloadPipeReport' || e.target.closest('#downloadPipeReport')) {
            handlePipeReportDownload();
        }
    });
    
    // Load example values on page load
    loadExample();
});

function loadExample() {
    // NPS 2", 1.034 MPa (150 psi), 260°C (500°F), A53B, seamless, threaded, 1.5875mm CA
    document.getElementById('nps').value = '2';
    document.getElementById('pressure_mpa').value = '1.034';
    document.getElementById('temp_c').value = '260';
    document.getElementById('material').value = 'A53B';
    document.getElementById('weld_type').value = 'S';
    document.getElementById('material_type').value = 'ferritic';
    document.getElementById('corrosion_mm').value = '1.5875';
    document.getElementById('threaded').value = 'true';
    document.getElementById('mill_tolerance').value = '12.5';
}

async function handlePipeCalculate(e) {
    e.preventDefault();
    const resultsArea = document.getElementById('pipeResults');
    resultsArea.classList.add('hidden');
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calculating...';

    const payload = {
        nps: parseFloat(document.getElementById('nps').value),
        pressure_mpa: parseFloat(document.getElementById('pressure_mpa').value),
        temp_c: parseFloat(document.getElementById('temp_c').value),
        material: document.getElementById('material').value,
        weld_type: document.getElementById('weld_type').value,
        material_type: document.getElementById('material_type').value,
        corrosion_mm: parseFloat(document.getElementById('corrosion_mm').value),
        threaded: document.getElementById('threaded').value === 'true',
        mill_tolerance: parseFloat(document.getElementById('mill_tolerance').value)
    };
    
    const dextOverride = document.getElementById('dext_override').value;
    const sAllowOverride = document.getElementById('s_allow_override').value;
    
    if (dextOverride) payload.dext_override = parseFloat(dextOverride);
    if (sAllowOverride) payload.s_allow_override = parseFloat(sAllowOverride);
    
    // Save the input data
    lastPipeInput = {...payload};

    try {
        const res = await fetch('/api/calculate-pipe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (!res.ok) {
            const errData = await res.json();
            alert(errData.error || 'Calculation failed');
            return;
        }
        
        const data = await res.json();
        lastPipeResult = data;
        renderPipeResults(data);
        resultsArea.classList.remove('hidden');
        
    } catch (err) {
        console.error('Error:', err);
        alert('Error connecting to server');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

async function handlePipeReportDownload() {
    if (!lastPipeResult || !lastPipeInput) {
        alert('Please calculate a result first');
        return;
    }
    
    try {
        const res = await fetch('/api/pipe-report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                input_data: lastPipeInput,
                result_data: lastPipeResult
            })
        });
        
        if (!res.ok) {
            alert('Failed to generate report');
            return;
        }
        
        // Download the file
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const filename = res.headers.get('Content-Disposition')?.split('filename=')[1] || 'Pipe_Wall_Report.pdf';
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
    } catch (err) {
        console.error('Error:', err);
        alert('Error downloading report');
    }
}

function renderPipeResults(data) {
    // Update metric values
    document.getElementById('r-tdis').textContent = data.t_dis_mm.toFixed(3);
    document.getElementById('r-treq').textContent = data.t_req_mm.toFixed(3);
    document.getElementById('r-tmin').textContent = data.t_min_mm.toFixed(3);
    document.getElementById('r-S').textContent = data.S_mpa.toFixed(2);
    
    // Status badge
    const statusBadge = document.getElementById('status-badge');
    let statusText = 'PASS';
    let statusClass = 'status-pass';
    
    if (!data.recommended_schedule) {
        statusText = 'NO SCHEDULE FOUND';
        statusClass = 'status-fail';
    } else if (!data.thin_wall_ok) {
        statusText = 'THICK WALL';
        statusClass = 'status-warning';
    }
    
    statusBadge.textContent = statusText;
    statusBadge.className = `status-badge ${statusClass}`;
    
    // Recommended schedule
    const scheduleGrid = document.getElementById('recommended-schedule');
    scheduleGrid.innerHTML = '';
    
    if (data.schedules && data.schedules.length > 0) {
        data.schedules.forEach(sched => {
            const item = document.createElement('div');
            item.className = `schedule-item ${sched.adequate ? 'adequate' : 'inadequate'}`;
            item.innerHTML = `
                <div class="schedule-name">SCH ${sched.schedule}</div>
                <div class="schedule-thickness">${sched.thickness_mm.toFixed(2)} mm</div>
            `;
            if (data.recommended_schedule && sched.schedule === data.recommended_schedule.schedule) {
                item.classList.add('recommended');
            }
            scheduleGrid.appendChild(item);
        });
    }
    
    // Thick wall warning
    const warning = document.getElementById('thick-wall-warning');
    if (!data.thin_wall_ok) {
        warning.classList.remove('hidden');
    } else {
        warning.classList.add('hidden');
    }
}