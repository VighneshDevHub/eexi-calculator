/**
 * main.js — EEXI Calculator frontend logic
 * Handles form submission, API call, and results rendering.
 */

// ── Ship types that use GT instead of DWT ───────────────────────────────
const GT_SHIP_TYPES = new Set(["ro_ro_pass", "cruise"]);

// ── DOM references ───────────────────────────────────────────────────────
const form        = document.getElementById("eexi-form");
const shipSel     = document.getElementById("ship_type");
const dwtGroup    = document.getElementById("dwt-group");
const gtGroup     = document.getElementById("gt-group");
const dwtInput    = document.getElementById("dwt");
const gtInput     = document.getElementById("gt");
const calcBtn     = document.getElementById("calc-btn");
const btnText     = document.getElementById("btn-text");
const btnSpinner  = document.getElementById("btn-spinner");
const formError   = document.getElementById("form-error");
const resultsPanel = document.getElementById("results-panel");

// ── Toggle DWT / GT fields based on ship type ────────────────────────────
function updateCapacityField() {
  const isGT = GT_SHIP_TYPES.has(shipSel.value);
  dwtGroup.classList.toggle("hidden", isGT);
  gtGroup.classList.toggle("hidden", !isGT);
  dwtInput.required = !isGT;
  gtInput.required  = isGT;
}

shipSel.addEventListener("change", updateCapacityField);
updateCapacityField();   // run on page load

// ── Form submission ──────────────────────────────────────────────────────
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearError();
  setLoading(true);

  const payload = buildPayload();
  if (!payload) { setLoading(false); return; }

  try {
    const res  = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!res.ok) {
      showError(data.error || "An error occurred. Please check your inputs.");
    } else {
      renderResults(data);
    }
  } catch (err) {
    showError("Network error — could not reach the server.");
  } finally {
    setLoading(false);
  }
});

// ── Build JSON payload from form ─────────────────────────────────────────
function buildPayload() {
  const isGT  = GT_SHIP_TYPES.has(shipSel.value);
  const dwt   = parseFloat(dwtInput.value) || 0;
  const gt    = parseFloat(gtInput.value)  || 0;
  const mcr   = parseFloat(document.getElementById("mcr").value);
  const sfc   = parseFloat(document.getElementById("sfc").value);
  const v_ref = parseFloat(document.getElementById("v_ref").value);

  if (isGT && gt <= 0)  { showError("Please enter a valid GT value."); return null; }
  if (!isGT && dwt <= 0) { showError("Please enter a valid DWT value."); return null; }
  if (!mcr || mcr <= 0) { showError("MCR must be a positive number."); return null; }
  if (!sfc || sfc <= 0) { showError("SFC must be a positive number."); return null; }
  if (!v_ref || v_ref <= 0) { showError("Design speed must be a positive number."); return null; }

  return {
    ship_type:  shipSel.value,
    dwt:        dwt,
    gt:         gt,
    mcr:        mcr,
    sfc:        sfc,
    fuel_type:  document.getElementById("fuel_type").value,
    v_ref:      v_ref,
    pae:        parseFloat(document.getElementById("pae").value)    || 0,
    sfc_ae:     parseFloat(document.getElementById("sfc_ae").value) || 0,
    fuel_ae:    document.getElementById("fuel_ae").value,
  };
}

// ── Render results into the results panel ────────────────────────────────
function renderResults(d) {
  const attained = d.attained_eexi;
  const required = d.required_eexi;
  const margin   = d.compliance.margin;
  const status   = d.compliance.status;

  // Status banner
  const banner = document.getElementById("status-banner");
  const icon   = document.getElementById("status-icon");
  const text   = document.getElementById("status-text");

  banner.className = "status-banner";
  if (status === "COMPLIANT") {
    banner.classList.add("status-compliant");
    icon.textContent = "✓";
    text.textContent = `COMPLIANT — ${margin.toFixed(1)}% below required EEXI`;
  } else if (status === "BORDERLINE") {
    banner.classList.add("status-borderline");
    icon.textContent = "⚠";
    text.textContent = `BORDERLINE — within 5% of required EEXI limit`;
  } else {
    banner.classList.add("status-noncompliant");
    icon.textContent = "✗";
    text.textContent = `NON-COMPLIANT — Engine Power Limitation required`;
  }

  // Metrics
  document.getElementById("r-attained").textContent = attained.toFixed(3);
  document.getElementById("r-required").textContent = required.toFixed(3);
  const marginEl = document.getElementById("r-margin");
  marginEl.textContent = (margin >= 0 ? "+" : "") + margin.toFixed(1);
  marginEl.style.color = margin >= 0 ? "var(--green-mid)" : "var(--red)";

  // Gauge
  const maxVal = Math.max(attained, required) * 1.3;
  const fillPct = Math.min((attained / maxVal) * 100, 100);
  const reqPct  = Math.min((required / maxVal) * 100, 100);
  const fill = document.getElementById("gauge-fill");
  fill.style.width = fillPct.toFixed(1) + "%";
  fill.style.background = status === "COMPLIANT" ? "var(--green-light)"
                        : status === "BORDERLINE" ? "var(--amber)"
                        : "var(--red)";
  document.getElementById("gauge-req-line").style.left = reqPct.toFixed(1) + "%";

  // Breakdown
  document.getElementById("r-pme").textContent   = d.pme.toLocaleString();
  document.getElementById("r-me-em").textContent  = d.me_emissions.toLocaleString();
  document.getElementById("r-ae-em").textContent  = d.ae_emissions.toLocaleString();
  document.getElementById("r-num").textContent    = d.numerator.toLocaleString();
  document.getElementById("r-cap").textContent    = d.capacity.toLocaleString();
  document.getElementById("r-cf").textContent     = d.cf_me;

  // EPL
  const eplSection = document.getElementById("epl-section");
  if (d.epl && !d.compliance.compliant) {
    eplSection.classList.remove("hidden");
    if (d.epl.epl_possible) {
      document.getElementById("r-epl-pme").textContent = d.epl.max_pme.toLocaleString();
      document.getElementById("r-epl-mcr").textContent = d.epl.limited_mcr.toLocaleString();
      document.getElementById("r-epl-pct").textContent = d.epl.epl_percentage
        ? d.epl.epl_percentage.toFixed(1) : "--";
    } else {
      document.getElementById("r-epl-pme").textContent = "N/A";
      document.getElementById("r-epl-mcr").textContent = "N/A";
      document.getElementById("r-epl-pct").textContent = "N/A";
    }
    document.getElementById("epl-note").textContent = d.epl.note;
  } else {
    eplSection.classList.add("hidden");
  }

  // Show panel
  resultsPanel.classList.remove("hidden");
  resultsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ── Utility ──────────────────────────────────────────────────────────────
function setLoading(on) {
  calcBtn.disabled = on;
  btnText.classList.toggle("hidden", on);
  btnSpinner.classList.toggle("hidden", !on);
}

function showError(msg) {
  formError.textContent = msg;
  formError.classList.remove("hidden");
}

function clearError() {
  formError.classList.add("hidden");
  formError.textContent = "";
}

function resetForm() {
  form.reset();
  updateCapacityField();
  clearError();
  resultsPanel.classList.add("hidden");
  window.scrollTo({ top: 0, behavior: "smooth" });
}
