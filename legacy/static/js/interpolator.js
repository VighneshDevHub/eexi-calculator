const FIELDS = ['x1', 'y1', 'x2', 'y2', 'x3', 'y3'];
let currentResult = null;

function getFieldValue(id) {
    const el = document.getElementById(id);
    return el && el.value.trim() !== '' ? parseFloat(el.value) : null;
}

function setFieldValue(id, val) {
    const el = document.getElementById(id);
    if (el) el.value = val === null || val === undefined ? '' : val;
}

function onFieldInput(el, field) {
    FIELDS.forEach(f => {
        const inputEl = document.getElementById(f);
        if (inputEl) inputEl.classList.remove('is-blank', 'is-computed');
    });
    hideError();
    hideResults();
}

function hideError() {
    const el = document.getElementById('form-error');
    if (el) {
        el.textContent = '';
        el.classList.add('hidden');
    }
}

function showError(msg) {
    const el = document.getElementById('form-error');
    if (el) {
        el.textContent = msg;
        el.classList.remove('hidden');
    }
}

function hideResults() {
    const el = document.getElementById('results-panel');
    if (el) el.classList.add('hidden');
    currentResult = null;
}

function showResults(data) {
    currentResult = data;
    
    const panel = document.getElementById('results-panel');
    const answerLabel = document.getElementById('answer-label');
    const answerValue = document.getElementById('answer-value');
    const formulaUsed = document.getElementById('formula-used');
    const stepsList = document.getElementById('steps-list');
    
    if (panel) panel.classList.remove('hidden');
    
    if (answerLabel) answerLabel.textContent = data.blank_field;
    if (answerValue) answerValue.textContent = data.result_str;
    if (formulaUsed) formulaUsed.textContent = data.formula_used;
    
    if (stepsList) {
        stepsList.innerHTML = '';
        data.steps.forEach(step => {
            const li = document.createElement('li');
            li.textContent = step;
            stepsList.appendChild(li);
        });
    }
    
    for (const f of FIELDS) {
        const cvEl = document.getElementById('cv-' + f);
        const inputEl = document.getElementById(f);
        if (cvEl) cvEl.textContent = data.all_values[f];
        if (inputEl) {
            inputEl.classList.remove('is-blank', 'is-computed');
            if (f === data.blank_field) {
                inputEl.classList.add('is-computed');
                inputEl.value = data.result_str;
            }
        }
    }
}

async function calculate() {
    const btn = document.getElementById('calc-btn');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    
    hideError();
    hideResults();
    
    const data = {};
    let blankCount = 0;
    FIELDS.forEach(f => {
        const v = getFieldValue(f);
        if (v === null) {
            blankCount++;
        } else {
            data[f] = v;
        }
    });
    
    if (blankCount !== 1) {
        showError('Exactly one field must be left blank');
        return;
    }
    
    if (btn) btn.disabled = true;
    if (btnText) btnText.classList.add('hidden');
    if (btnSpinner) btnSpinner.classList.remove('hidden');
    
    try {
        const res = await fetch('/api/calculate-interpolator', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        if (!res.ok) {
            showError(result.error || 'Calculation failed');
        } else {
            showResults(result);
        }
    } catch (err) {
        console.error(err);
        showError('Network error, please try again');
    } finally {
        if (btn) btn.disabled = false;
        if (btnText) btnText.classList.remove('hidden');
        if (btnSpinner) btnSpinner.classList.add('hidden');
    }
}

function loadExample() {
    setFieldValue('x1', 10);
    setFieldValue('y1', 20);
    setFieldValue('x2', 20);
    setFieldValue('y2', 50);
    setFieldValue('x3', 15);
    setFieldValue('y3', '');
    onFieldInput();
}

function resetAll() {
    FIELDS.forEach(f => setFieldValue(f, ''));
    onFieldInput();
}
