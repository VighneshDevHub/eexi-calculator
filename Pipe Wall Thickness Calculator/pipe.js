cat > /home/claude/eexi_project/static/js/pipe.js << 'JSEOF'
/**
 * pipe.js — ASME B31.3 §304.1.2 Pipe Wall Thickness Calculator frontend
 * All reference data injected from Flask via template variables.
 */

"use strict";

// ── Unit conversions ─────────────────────────────────────────────────────────
function psiToMpa() {
  const psi = parseFloat(document.getElementById("conv_psi").value);
  if (!isNaN(psi)) {
    document.getElementById("conv_mpa").value = (psi * 0.00689476).toFixed(4);
  }
}
function mpaToPsi() {
  const mpa = parseFloat(document.getElementById("conv_mpa").value);
  if (!isNaN(mpa)) {
    document.getElementById("conv_psi").value = (mpa / 0.00689476).toFixed(1);
  }
}
function fToC() {
  const f = parseFloat(document.getElementById("conv_f").value);
  if (!isNaN(f)) {
    document.getElementById("conv_c").value = ((f - 32) * 5 / 9).toFixed(1);
  }
}
function cToF() {
  const c = parseFloat(document.getElementById("conv_c").value);
  if (!isNaN(c)) {
    document.getElementById("conv_f").value = (c * 9 / 5 + 32).toFixed(1);
  }
}

// ── Auto-interpolate allowable stress ────────────────────────────────────────
const TEMP_BREAKPOINTS = TEMP_COLS;

function interpStress(matKey, tempC) {
  const row = MATERIAL_STRESS[matKey];
  if (!row) return null;
  const t = Math.max(37.78, tempC);
  for (let i = 0; i < TEMP_BREAKPOINTS.length - 1; i++) {
    if (t <= TEMP_BREAKPOINTS[i + 1]) {
      const sA = row[i], sB = row[i + 1];
      if (sA == null) return null;
      if (sB == null) return parseFloat(sA.toFixed(4));
      return sA + (sB - sA) * (t - TEMP_BREAKPOINTS[i]) / (TEMP_BREAKPOINTS[i + 1] - TEMP_BREAKPOINTS[i]);
    }
  }
  for (let i = row.length - 1; i >= 0; i--) {
    if (row[i] != null) return parseFloat(row[i]);
  }
  return null;
}

function updateAutoStress() {
  const mat   = document.getElementById("material").value;
  const tempC = parseFloat(document.getElementById("temp_c").value);
  const s     = isNaN(tempC) ? null : interpStress(mat, tempC);
  const el    = document.getElementById("auto-stress");
  const tEl   = document.getElementById("auto-stress-t");
  if (s) {
    el.textContent = s.toFixed(3);
    tEl.textContent = isNaN(tempC) ? "—" : tempC;
  } else {
    el.textContent = "—";
    tEl.textContent = "—";
  }
}

document.getElementById("material").addEventListener("change", updateAutoStress);
document.getElementById("temp_c").addEventListener("input", updateAutoStress);

// ── NPS change ───────────────────────────────────────────────────────────────
function onNPSChange() {
  const nps  = parseFloat(document.getElementById("nps").value);
  const dext = NPS_DEXT[nps];
  document.getElementById("dext-hint").textContent =
    dext ? `Standard OD = ${dext} mm (ASME B36.10M)` : "";
  onThreadChange();
}

function onMaterialChange() {
  updateAutoStress();
}

function onThreadChange() {
  const threaded = document.getElementById("threaded").value === "true";
  const nps      = parseFloat(document.getElementById("nps").value);
  const td       = THREAD_DEPTH[nps];
  const hint     = document.getElementById("thread-depth-hint");
  if (threaded && td) {
    hint.textContent = `TD = ${td.toFixed(3)} mm (ASME B1.20.1, NPS ${nps}")`;
  } else {
    hint.textContent = "";
  }
}

// ── Pressure hint ─────────────────────────────────────────────────────────────
document.getElementById("pressure_mpa").addEventListener("input", function() {
  const mpa = parseFloat(this.value);
  document.getElementById("pressure_psi_hint").textContent =
    isNaN(mpa) ? "" : `≈ ${(mpa / 0.00689476).toFixed(0)} psi`;
});

document.getElementById("temp_c").addEventListener("input", function() {
  const c = parseFloat(this.value);
  document.getElementById("temp_f_hint").textContent =
    isNaN(c) ? "" : `≈ ${(c * 9 / 5 + 32).toFixed(0)} °F`;
});

// ── Load worked example (matches Excel sheet "14. Example") ──────────────────
function loadExample() {
  document.getElementById("nps").value          = "2";
  document.getElementById("pressure_mpa").value = "1.0342";
  document.getElementById("temp_c").value       = "260";
  document.getElementById("material").value     = "A53B";
  document.getElementById("weld_type").value    = "S";
  document.getElementById("material_type").value= "ferritic";
  document.getElementById("corrosion_mm").value = "1.5875";
  document.getElementById("threaded").value     = "true";
  document.getElementById("mill_tolerance").value = "12.5";
  document.getElementById("dext_override").value  = "";
  document.getElementById("s_allow_override").value = "";
  onNPSChange();
  onThreadChange();
  updateAutoStress();
  document.getElementById("pressure_psi_hint").textContent = "≈ 150 psi";
  document.getElementById("temp_f_hint").textContent = "≈ 500 °F";
  clearError();
  document.getElementById("results-panel").classList.add("hidden");
  document.getElementById("guidance-card").classList.remove("hidden");
}

// ── Calculate ─────────────────────────────────────────────────────────────────
async function calculate() {
  clearError();

  const nps      = parseFloat(document.getElementById("nps").value);
  const P        = parseFloat(document.getElementById("pressure_mpa").value);
  const tempC    = parseFloat(document.getElementById("temp_c").value);
  const material = document.getElementById("material").value;
  const weld     = document.getElementById("weld_type").value;
  const CA       = parseFloat(document.getElementById("corrosion_mm").value) || 0;
  const threaded = document.getElementById("threaded").value === "true";
  const MT       = parseFloat(document.getElementById("mill_tolerance").value) || 12.5;
  const matType  = document.getElementById("material_type").value;
  const sOver    = parseFloat(document.getElementById("s_allow_override").value) || null;
  const dextOver = parseFloat(document.getElementById("dext_override").value) || null;

  if (isNaN(P) || P < 0)     return showError("Design pressure must be a non-negative number.");
  if (isNaN(tempC))           return showError("Design temperature is required.");
  if (!material)              return showError("Select a pipe material.");

  const payload = {
    nps, pressure_mpa: P, temp_c: tempC, material,
    weld_type: weld, corrosion_mm: CA, threaded,
    mill_tolerance: MT, material_type: matType,
    ...(sOver    ? { s_allow_override: sOver }    : {}),
    ...(dextOver ? { dext_override: dextOver }    : {}),
  };

  setLoading(true);
  try {
    const res  = await fetch("/api/calculate-pipe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) { showError(data.error || "Calculation failed."); return; }
    renderResults(data);
  } catch {
    showError("Network error — could not reach the server.");
  } finally {
    setLoading(false);
  }
}

// ── Render results ────────────────────────────────────────────────────────────
function renderResults(d) {
  // Metrics
  document.getElementById("r-tdis").textContent = d.t_dis_mm.toFixed(4);
  document.getElementById("r-treq").textContent = d.t_req_mm.toFixed(4);
  document.getElementById("r-tmin").textContent = d.t_min_mm.toFixed(4);
  document.getElementById("r-S").textContent    = d.S_mpa.toFixed(3);
  document.getElementById("r-S-sub").textContent = d.S_source;
  document.getElementById("r-nps-label").textContent = d.nps_label;

  // Schedule grid
  const grid = document.getElementById("sch-grid");
  grid.innerHTML = d.schedules.map(s => {
    const cls = s.adequate ? "sch-pill sch-ok" : "sch-pill sch-no";
    const first = d.recommended_schedule && s.schedule === d.recommended_schedule.schedule;
    return `<div class="${cls}${first ? " sch-first" : ""}">
      <div class="sch-pill-name">Sch ${s.schedule}</div>
      <div class="sch-pill-t">${s.thickness_mm} mm</div>
      ${first ? '<div class="sch-pill-tag">✓ min</div>' : ""}
    </div>`;
  }).join("");

  // Status banner
  const banner = document.getElementById("status-banner");
  if (d.recommended_schedule) {
    banner.className = "status-banner status-compliant";
    banner.innerHTML = `<span class="status-icon">✓</span>
      <div class="status-body">
        <div class="status-text">Minimum schedule: Sch ${d.recommended_schedule.schedule}
          (t = ${d.recommended_schedule.thickness_mm} mm)</div>
        <div class="status-sub">t<sub>min</sub> required = ${d.t_min_mm.toFixed(4)} mm &nbsp;&middot;&nbsp;
          ${d.nps_label} ${d.material_label} &nbsp;&middot;&nbsp; ${d.weld_type}</div>
      </div>`;
  } else {
    banner.className = "status-banner status-noncompliant";
    banner.innerHTML = `<span class="status-icon">✗</span>
      <div class="status-body">
        <div class="status-text">No standard schedule satisfies t<sub>min</sub> = ${d.t_min_mm.toFixed(4)} mm</div>
        <div class="status-sub">Specify a custom wall thickness or reduce allowances.</div>
      </div>`;
  }

  // Thin-wall warning
  const twWarn = document.getElementById("thick-wall-warn");
  twWarn.classList.toggle("hidden", d.thin_wall_ok);

  // Step-by-step
  buildSteps(d);

  // Show
  document.getElementById("results-panel").classList.remove("hidden");
  document.getElementById("guidance-card").classList.add("hidden");
  document.getElementById("results-panel").scrollIntoView({ behavior: "smooth", block: "start" });
}

function buildSteps(d) {
  const steps = [
    {
      n: 1, title: "Pipe exterior diameter (ASME B36.10M)",
      formula: `d<sub>ext</sub> = ${d.dext_mm} mm &nbsp; (NPS ${d.nps_label})`,
      note: "Standard dimension from ASME B36.10M table"
    },
    {
      n: 2, title: "Material allowable stress S (Table A-1, ASME B31.3)",
      formula: `S = ${d.S_mpa.toFixed(4)} MPa &nbsp; at ${d.temp_c}°C &nbsp; (${d.material_label})`,
      note: d.S_source
    },
    {
      n: 3, title: "Quality factor E (Table A-1B)",
      formula: `E = ${d.E_factor} &nbsp; (weld type: ${d.weld_type})`,
      note: "S=ERW=EFW: E=1.0 &nbsp;|&nbsp; FBW: E=0.6"
    },
    {
      n: 4, title: "Y coefficient (Table 304.1.1)",
      formula: `Y = ${d.Y_coeff.toFixed(2)} &nbsp; at ${d.temp_c}°C`,
      note: `Valid for thin-wall: t &lt; d/6 = ${d.thin_wall_limit_mm} mm &nbsp; ${d.thin_wall_ok ? "✓ confirmed" : "⚠ check thick-wall"}`
    },
    {
      n: 5, title: "Pressure design thickness t<sub>dis</sub> — Eq. 3a (§304.1.2)",
      formula: `t<sub>dis</sub> = P &times; d<sub>ext</sub> / (2 &times; (S&times;E + P&times;Y))
               = ${d.pressure_mpa} &times; ${d.dext_mm} / (2 &times; (${d.S_mpa.toFixed(4)}&times;${d.E_factor} + ${d.pressure_mpa}&times;${d.Y_coeff}))
               = <strong>${d.t_dis_mm.toFixed(4)} mm</strong>`,
      note: ""
    },
    {
      n: 6, title: "Over-thickness allowance OT",
      formula: `TC (corrosion) = ${d.CA_mm} mm${d.threaded ? `<br>TD (thread depth, ASME B1.20.1) = ${d.TD_mm.toFixed(4)} mm` : ""}
               <br>OT = ${d.OT_mm.toFixed(4)} mm`,
      note: d.threaded ? `NPT thread depth for NPS ${d.nps_label}` : "Plain end — no thread allowance"
    },
    {
      n: 7, title: "Required thickness t<sub>req</sub> (§304.1.1 Eq. 2)",
      formula: `t<sub>req</sub> = t<sub>dis</sub> + OT = ${d.t_dis_mm.toFixed(4)} + ${d.OT_mm.toFixed(4)} = <strong>${d.t_req_mm.toFixed(4)} mm</strong>`,
      note: ""
    },
    {
      n: 8, title: `Mill tolerance MT = ${d.mill_tolerance}% (ASTM A53/A106 — Sheet 7.MT)`,
      formula: `t<sub>min</sub> = t<sub>req</sub> &times; 100 / (100 &minus; MT)
               = ${d.t_req_mm.toFixed(4)} &times; 100 / ${100 - d.mill_tolerance}
               = <strong>${d.t_min_mm.toFixed(4)} mm</strong>`,
      note: "This is the minimum nominal wall thickness to specify on the purchase order"
    },
    ...(d.recommended_schedule ? [{
      n: 9, title: "Schedule selection (ASME B36.10M)",
      formula: `Select Sch <strong>${d.recommended_schedule.schedule}</strong> &rarr; actual t = ${d.recommended_schedule.thickness_mm} mm &ge; t<sub>min</sub> = ${d.t_min_mm.toFixed(4)} mm &nbsp; ✓`,
      note: `NPS ${d.nps_label} per ASME B36.10M`
    }] : []),
  ];

  document.getElementById("steps-list").innerHTML = steps.map(s => `
    <div class="pipe-step">
      <div class="pipe-step-num">${s.n}</div>
      <div class="pipe-step-body">
        <div class="pipe-step-title">${s.title}</div>
        <div class="pipe-step-formula">${s.formula}</div>
        ${s.note ? `<div class="pipe-step-note">${s.note}</div>` : ""}
      </div>
    </div>
  `).join("");
}

// ── Utilities ─────────────────────────────────────────────────────────────────
function setLoading(on) {
  document.getElementById("calc-btn").disabled = on;
  document.getElementById("btn-text").classList.toggle("hidden", on);
  document.getElementById("btn-spinner").classList.toggle("hidden", !on);
}
function showError(msg) {
  const el = document.getElementById("form-error");
  el.textContent = msg;
  el.classList.remove("hidden");
}
function clearError() {
  document.getElementById("form-error").classList.add("hidden");
}
function resetAll() {
  clearError();
  document.getElementById("results-panel").classList.add("hidden");
  document.getElementById("guidance-card").classList.remove("hidden");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// ── Init ──────────────────────────────────────────────────────────────────────
onNPSChange();
updateAutoStress();
JSEOF
echo "pipe.js OK"
Output

pipe.js OK