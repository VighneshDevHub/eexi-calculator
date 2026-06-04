/**
 * cii.js — CII Calculator frontend logic
 * MEPC.352(78) with correction factors from MEPC.355(78)
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
const boilerSect = document.getElementById("boiler-section");
const calcBtn    = document.getElementById("cii-calc-btn");
const btnText    = document.getElementById("cii-btn-text");
const btnSpinner = document.getElementById("cii-btn-spinner");
const formError  = document.getElementById("cii-form-error");
const results    = document.getElementById("cii-results-panel");

// ── Ship type change ──────────────────────────────────────────────────────────
function onCIIShipChange() {
  const t = shipSel.value;
  const isGT     = GT_TYPES.has(t);
  const isTanker = TANKER_TYPES.has(t);

  dwtGroup.classList.toggle("hidden", isGT);
  gtGroup.classList.toggle("hidden",  !isGT);
  dwtInput.required = !isGT;
  gtInput.required  = isGT;

  stsSection.style.display  = isTanker ? "" : "none";
  boilerSect.style.display  = isTanker ? "" : "none";
}

shipSel.addEventListener("change", onCIIShipChange);
onCIIShipChange();

// ── Load example ──────────────────────────────────────────────────────────────
function loadCIIExample() {
  shipSel.value = "bulk_carrier";
  onCIIShipChange();
  dwtInput.value   = 75000;
  document.getElementById("year").value = 2024;
  document.getElementById("distance_nm").value = 120000;
  document.getElementById("fc_hfo").value = 8500;
  document.getElementById("fc_mdo").value = 200;
  clearError();
  results.classList.add("hidden");
}

// ── Form submit ───────────────────────────────────────────────────────────────
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
  } catch {
    showError("Network error — could not reach the server.");
  } finally {
    setLoading(false);
  }
});

// ── Build payload ─────────────────────────────────────────────────────────────
function buildPayload() {
  const isGT = GT_TYPES.has(shipSel.value);
  const dwt  = parseFloat(dwtInput.value) || 0;
  const gt   = parseFloat(gtInput.value)  || 0;
  const dist = parseFloat(document.getElementById("distance_nm").value);

  if (isGT && gt <= 0)   { showError("Please enter a valid GT."); return null; }
  if (!isGT && dwt <= 0) { showError("Please enter a valid DWT."); return null; }
  if (!dist || dist <= 0){ showError("Annual distance sailed must be positive."); return null; }

  const fuelKeys = ["hfo","mdo","lng","methanol","lpg_propane"];
  const anyFuel  = fuelKeys.some(k => parseFloat(document.getElementById(`fc_${k}`)?.value) > 0);
  if (!anyFuel) { showError("Enter at least one fuel consumption value."); return null; }

  const tankerOp = document.getElementById("tanker_op")?.value || "none";

  return {
    ship_type:   shipSel.value,
    dwt, gt,
    year:        parseInt(document.getElementById("year").value),
    distance_nm: dist,

    // Fuels
    fc_hfo:        parseFloat(document.getElementById("fc_hfo").value)      || 0,
    fc_mdo:        parseFloat(document.getElementById("fc_mdo").value)      || 0,
    fc_lng:        parseFloat(document.getElementById("fc_lng").value)      || 0,
    fc_methanol:   parseFloat(document.getElementById("fc_methanol").value) || 0,

    // §4.1 voyage adjustments
    voyage_hfo:      parseFloat(document.getElementById("voyage_hfo").value)      || 0,
    voyage_mdo:      parseFloat(document.getElementById("voyage_mdo").value)      || 0,
    voyage_distance: parseFloat(document.getElementById("voyage_distance").value) || 0,

    // §4.2 STS/Shuttle
    sts_operation: tankerOp === "sts",
    shuttle_tanker: tankerOp === "shuttle",

    // §4.3 Electrical
    reefer_kwh:       parseFloat(document.getElementById("reefer_kwh").value)       || 0,
    reefer_days_sea:  parseFloat(document.getElementById("reefer_days_sea").value)  || 0,
    reefer_days_port: parseFloat(document.getElementById("reefer_days_port").value) || 0,
    sfoc_electrical:  parseFloat(document.getElementById("sfoc_electrical").value)  || 175,

    // §4.4–4.5 Boiler / others
    fc_boiler_hfo:  parseFloat(document.getElementById("fc_boiler_hfo").value)  || 0,
    fc_others_hfo:  parseFloat(document.getElementById("fc_others_hfo").value)  || 0,
  };
}

// ── Render results ────────────────────────────────────────────────────────────
const RATING_COLORS = { A:"#059669", B:"#10B981", C:"#F59E0B", D:"#EF4444", E:"#991B1B" };
const RATING_LABELS = {
  A: "Superior", B: "Minor Superior", C: "Moderate", D: "Minor Inferior", E: "Inferior"
};
// Approximate band marker positions (centre of each band in the 5-band strip)
const BAND_POSITIONS = { A: 10, B: 30, C: 50, D: 70, E: 90 };

function renderResults(d) {
  const rating  = d.rating.rating;
  const attained = d.attained_cii;
  const required = d.required_cii;
  const margin   = d.rating.margin_pct;
  const color    = RATING_COLORS[rating];

  // Year badge
  document.getElementById("cii-year-badge").textContent = `${d.year}`;

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
  const activeBand = document.querySelector(`.band-${rating.toLowerCase()}`);
  if (activeBand) {
    activeBand.classList.add("band-active");
    activeBand.style.background = color;
  }

  // Metrics
  document.getElementById("cii-r-attained").textContent = attained.toFixed(4);
  document.getElementById("cii-r-required").textContent = required.toFixed(4);
  const mEl = document.getElementById("cii-r-margin");
  mEl.textContent = (margin >= 0 ? "+" : "") + margin.toFixed(1);
  mEl.style.color = margin >= 0 ? "var(--green-mid)" : "var(--red)";

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

  // Regulatory note
  const noteEl = document.getElementById("cii-reg-note");
  const dd = d.reduction_factor_pct;
  const nextYear = d.year + 1;
  const nextDD = dd < 11 ? dd + 2 : 11;
  if (["D","E"].includes(rating)) {
    noteEl.innerHTML = `<strong>⚠ Action required:</strong> ${d.rating.description} The SEEMP must be updated with a corrective action plan. If the vessel receives D for 3 consecutive years or E for any year, the shipowner must submit a corrective action plan to the Administration. Current year reduction factor: <strong>${dd}%</strong> below 2019 baseline.`;
    noteEl.className = "reg-note reg-note-warn";
  } else {
    noteEl.innerHTML = `Reduction factor for ${d.year}: <strong>${dd}%</strong> below 2019 reference baseline. Target becomes <strong>${nextDD}%</strong> in ${nextYear}. Rated <strong>${rating} (${RATING_LABELS[rating]})</strong> — no mandatory corrective action required for this year.`;
    noteEl.className = "reg-note reg-note-ok";
  }

  results.classList.remove("hidden");
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ── Utility ───────────────────────────────────────────────────────────────────
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
function resetCIIForm() {
  form.reset();
  onCIIShipChange();
  clearError();
  results.classList.add("hidden");
  document.querySelectorAll(".band").forEach(b => {
    b.classList.remove("band-active");
    b.style.background = "";
  });
  window.scrollTo({ top: 0, behavior: "smooth" });
}
