/**
 * cii.js — CII Calculator frontend logic
 */

const GT_TYPES = new Set(["ro_ro_pass", "cruise"]);
const TANKER_TYPES = new Set(["tanker"]);

// ── DOM refs ─────────────────────────────────────────────────────────────────
const form       = document.getElementById("cii-form");
const shipSel    = document.getElementById("ship_type");
const dwtGroup   = document.getElementById("cii-dwt-group");
const gtGroup    = document.getElementById("cii-gt-group");
const dwtInput   = document.getElementById("dwt");
const gtInput    = document.getElementById("gt");
const stsSection = document.getElementById("sts-section");
const calcBtn    = document.getElementById("cii-calc-btn");
const btnText    = document.getElementById("cii-btn-text");
const btnSpinner = document.getElementById("cii-btn-spinner");
const formError  = document.getElementById("cii-form-error");
const results    = document.getElementById("cii-results-panel");

let lastCIIResult = null;

// ── Ship type change ──────────────────────────────────────────────────────────
function onCIIShipChange() {
  if (!shipSel) return;
  const t = shipSel.value;
  const isGT     = GT_TYPES.has(t);
  const isTanker = TANKER_TYPES.has(t);

  if (dwtGroup) dwtGroup.classList.toggle("hidden", isGT);
  if (gtGroup)  gtGroup.classList.toggle("hidden",  !isGT);
  if (dwtInput) dwtInput.required = !isGT;
  if (gtInput)  gtInput.required  = isGT;

  if (stsSection) {
    stsSection.style.display = isTanker ? "" : "none";
  }
}

if (shipSel) {
  shipSel.addEventListener("change", onCIIShipChange);
  onCIIShipChange();
}

// ── Load example ──────────────────────────────────────────────────────────────
function loadCIIExample() {
  if (shipSel) {
    shipSel.value = "bulk_carrier";
    onCIIShipChange();
  }
  if (dwtInput) dwtInput.value = 75000;
  
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.value = 2024;
  
  const distEl = document.getElementById("distance_nm");
  if (distEl) distEl.value = 120000;
  
  const hfoEl = document.getElementById("fc_hfo");
  if (hfoEl) hfoEl.value = 8500;
  
  const mdoEl = document.getElementById("fc_mdo");
  if (mdoEl) mdoEl.value = 200;

  // Add some correction factor examples
  const reeferEl = document.getElementById("reefer_kwh");
  if (reeferEl) reeferEl.value = 1500;
  
  const sfocElecEl = document.getElementById("sfoc_electrical");
  if (sfocElecEl) sfocElecEl.value = 190;

  clearError();
  if (results) results.classList.add("hidden");
}

function resetCIIForm() {
  form.reset();
  onCIIShipChange();
  clearError();
  results.classList.add("hidden");
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function clearError() {
  formError.textContent = "";
  formError.classList.add("hidden");
}

function showError(msg) {
  formError.textContent = msg;
  formError.classList.remove("hidden");
  formError.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function setLoading(isLoading) {
  calcBtn.disabled = isLoading;
  btnSpinner.classList.toggle("hidden", !isLoading);
  btnText.style.opacity = isLoading ? "0.5" : "1";
}

// ── Form submit ───────────────────────────────────────────────────────────────
if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError();
    setLoading(true);

    const payload = buildPayload();
    if (!payload) { setLoading(false); return; }

    try {
      const res  = await fetch("/api/calculate-cii", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        showError(data.error || "Calculation failed. Check your inputs.");
      } else {
        renderResults(data);
      }
    } catch (err) {
      console.error(err);
      showError("Network error — could not reach the server.");
    } finally {
      setLoading(false);
    }
  });
}

// ── Build payload ─────────────────────────────────────────────────────────────
function buildPayload() {
  if (!shipSel) return null;
  const isGT = GT_TYPES.has(shipSel.value);
  const dwt  = parseFloat(dwtInput?.value) || 0;
  const gt   = parseFloat(gtInput?.value)  || 0;
  const distEl = document.getElementById("distance_nm");
  const dist = distEl ? parseFloat(distEl.value) : 0;

  if (isGT && gt <= 0)   { showError("Please enter a valid GT."); return null; }
  if (!isGT && dwt <= 0) { showError("Please enter a valid DWT."); return null; }
  if (!dist || dist <= 0){ showError("Annual distance sailed must be positive."); return null; }

  const fuelKeys = ["fc_hfo", "fc_mdo", "fc_lng", "fc_methanol"];
  const anyFuel  = fuelKeys.some(k => {
    const el = document.getElementById(k);
    return el && parseFloat(el.value) > 0;
  });
  if (!anyFuel) { showError("Enter at least one fuel consumption value."); return null; }

  const tankerOp = document.getElementById("tanker_op")?.value || "none";
  const yearEl = document.getElementById("year");

  return {
    ship_type:   shipSel.value,
    dwt, gt,
    year:        yearEl ? parseInt(yearEl.value) : 2024,
    distance_nm: dist,

    // Fuels
    fc_hfo:        parseFloat(document.getElementById("fc_hfo")?.value)      || 0,
    fc_mdo:        parseFloat(document.getElementById("fc_mdo")?.value)      || 0,
    fc_lng:        parseFloat(document.getElementById("fc_lng")?.value)      || 0,
    fc_methanol:   parseFloat(document.getElementById("fc_methanol")?.value) || 0,

    // §4.1 voyage adjustments
    voyage_hfo:      parseFloat(document.getElementById("voyage_hfo")?.value)      || 0,
    voyage_distance: parseFloat(document.getElementById("voyage_distance")?.value) || 0,

    // §4.2 STS/Shuttle
    sts_operation: tankerOp === "sts",
    shuttle_tanker: tankerOp === "shuttle",

    // §4.3 Electrical
    reefer_kwh:       parseFloat(document.getElementById("reefer_kwh")?.value)       || 0,
    sfoc_electrical:  parseFloat(document.getElementById("sfoc_electrical")?.value)  || 175,
  };
}

// ── Render results ────────────────────────────────────────────────────────────
const RATING_COLORS = { A:"#059669", B:"#10B981", C:"#F59E0B", D:"#EF4444", E:"#991B1B" };
const RATING_LABELS = {
  A: "Superior", B: "Minor Superior", C: "Moderate", D: "Minor Inferior", E: "Inferior"
};
const BAND_POSITIONS = { A: 10, B: 30, C: 50, D: 70, E: 90 };

function renderResults(d) {
  lastCIIResult = d;
  const rating  = d.rating.rating;
  const attained = d.attained_cii;
  const required = d.required_cii;
  const margin   = d.rating.margin_pct;
  const color    = RATING_COLORS[rating];

  results.classList.remove("hidden");
  results.scrollIntoView({ behavior: 'smooth' });

  // Rating display
  const letter = document.getElementById("cii-rating-letter");
  letter.textContent  = rating;
  letter.style.color  = color;
  letter.style.borderColor = color;
  document.getElementById("cii-rating-label").textContent = RATING_LABELS[rating];
  document.getElementById("cii-rating-desc").textContent  = d.rating.description;

  // Band marker
  const marker = document.getElementById("band-marker");
  marker.style.left  = BAND_POSITIONS[rating] + "%";
  marker.style.color = color;

  // Highlight active band
  document.querySelectorAll(".band").forEach(b => b.classList.remove("band-active"));
  const bandKey = rating.toLowerCase();
  const activeBand = document.querySelector(`.band-${bandKey}`);
  if (activeBand) {
    activeBand.classList.add("band-active");
  }

  // Metrics
  document.getElementById("cii-r-attained").textContent = attained.toFixed(4);
  document.getElementById("cii-r-required").textContent = required.toFixed(4);
  const mEl = document.getElementById("cii-r-margin");
  mEl.textContent = (margin >= 0 ? "+" : "") + margin.toFixed(1) + "%";
  mEl.style.color = margin >= 0 ? "#059669" : "#ef4444";

  // Boundaries
  const b = d.rating.boundaries;
  document.getElementById("b-a").textContent = b.A.toFixed(4);
  document.getElementById("b-b").textContent = b.B.toFixed(4);
  document.getElementById("b-c").textContent = b.C.toFixed(4);
  document.getElementById("b-d").textContent = b.D.toFixed(4);

  // Corrections
  const corrSec  = document.getElementById("corrections-section");
  const corrList = document.getElementById("corrections-list");
  corrList.innerHTML = "";
  if (d.corrections_applied && d.corrections_applied.length > 0) {
    corrSec.classList.remove("hidden");
    d.corrections_applied.forEach(c => {
      const li = document.createElement("li");
      li.textContent = c;
      corrList.appendChild(li);
    });
  } else {
    corrSec.classList.add("hidden");
  }
}

async function downloadCIIReport() {
  if (!lastCIIResult) return;
  
  const btn = document.getElementById("download-cii-report");
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
  
  try {
    const res = await fetch("/api/cii-report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(lastCIIResult),
    });
    
    if (res.ok) {
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `CII_Report_${lastCIIResult.year}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } else {
      alert("Failed to generate report.");
    }
  } catch (err) {
    console.error(err);
    alert("Error generating report.");
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalHtml;
  }
}
