# IMO Ship Emissions & Engineering Calculator

A full-stack web application for maritime compliance and engineering calculations, covering **EEXI**, **CII**, **Exhaust Gas Back Pressure (EGBP)**, and **Pipe Wall Thickness** — core engineering assessments required under IMO MARPOL Annex VI regulations and ASME B31.3. Built for naval architects, ship operators, and class society engineers.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Features](#3-features)
4. [Technical Architecture](#4-technical-architecture)
5. [Technology Stack](#5-technology-stack)
6. [Project Structure](#6-project-structure)
7. [Calculators — Technical Detail](#7-calculators--technical-detail)
   - [EEXI Calculator](#71-eexi-calculator)
   - [CII Calculator](#72-cii-calculator)
   - [EGBP Calculator](#73-egbp-calculator)
   - [Pipe Wall Thickness Calculator](#74-pipe-wall-thickness-calculator)
8. [Database Schema](#8-database-schema)
9. [API Reference](#9-api-reference)
10. [Installation & Setup](#10-installation--setup)
11. [Running the Application](#11-running-the-application)
12. [Regulatory References](#12-regulatory-references)
13. [Known Issues & Bug Fixes](#13-known-issues--bug-fixes)
14. [Future Roadmap](#14-future-roadmap)

---

## 1. Project Overview

This project was developed as part of an engineering internship at **Goltens** to digitize manual IMO compliance and piping engineering calculations that were previously done with spreadsheets and handbooks. The tool provides instant, auditable results for four distinct engineering assessments, with PDF report generation and a full calculation history log.

**Version:** 2.0.0  
**Framework:** Flask (Python)  
**Database:** SQLite (via SQLAlchemy)  
**Frontend:** Jinja2 templates + vanilla JS  

---

## 2. Problem Statement

Since January 2023, all ships above 400 GT engaged in international voyages must comply with two new IMO regulations:

- **EEXI (Energy Efficiency Existing Ship Index):** A one-time technical baseline compliance check — similar to a carbon rating for the ship's design.
- **CII (Carbon Intensity Indicator):** An annual operational rating (A–E) that tracks how efficiently a ship actually operates year over year.

Additionally, marine engineers frequently need to assess:
- **Exhaust Gas Back Pressure** in the exhaust ducting systems to ensure engine performance is not compromised by poorly designed pipework.
- **Pipe Wall Thickness** to determine the minimum required wall thickness and ASME schedule selection for process and utility piping under pressure and temperature.

**Before this tool:** Engineers performed these calculations manually in Excel, referencing multiple IMO resolution tables, ASME B31.3 code books, and Wärtsilä engineering documents. This process was:
- Error-prone (manual transcription, wrong table lookups)
- Time-consuming (30–90 minutes per vessel or system)
- Difficult to audit or version-control

**This tool solves all four problems** — calculations execute in under a second, all inputs/outputs are stored in a database, and PDF reports are generated on demand.

---

## 3. Features

### EEXI Calculator
- Full EEXI attained/required calculation per IMO MEPC.350(78)
- Supports all 9 IMO ship types (bulk carrier, tanker, container, general cargo, ro-ro cargo, ro-ro passenger, LNG carrier, gas carrier, cruise)
- Supports 7 fuel types with correct CO2 conversion factors (MARPOL Annex VI Reg. 2)
- Optional auxiliary engine (PAE) inclusion with separate fuel type and SFC
- All 6 correction factors: f_eff, f_i, f_w, f_c, f_l, f_m
- EPL (Engine Power Limitation) / MCRlim calculation — iterative solver with speed adjustment
- Compliance margin expressed as a percentage
- PDF report generation per vessel

### CII Calculator
- Annual CII rating (A / B / C / D / E) per IMO MEPC.352–355(78)
- Multi-fuel input (HFO, MDO, LNG, Methanol, LPG Propane, LPG Butane, Ethane)
- Reduction factor applied per year (2023–2027+)
- Ship-type specific rating boundaries (d-vector from MEPC.354(78))
- Tanker correction factors: STS operation, shuttle tanker mode
- Reefer energy deductions: monitored (kWh-based) and unmonitored (day-based)
- Boiler and pump fuel deductions (tankers)
- Voyage deductions (port calls not counted)
- PDF report with rating boundaries table and corrections log

### EGBP Calculator
- Pressure loss calculation across complex exhaust pipe networks
- Supports 15 element types: straight pipe, bends, diffusers, valves, silencers, boilers, wye junctions, orifices, and custom elements
- Colebrook-White friction factor solver (100-iteration convergence)
- Exhaust gas density and kinematic viscosity calculated from temperature
- Engine presets for Main Engine, Auxiliary Engines, and Oil Fired Boilers
- Pass / Borderline / Fail status with 85% utilisation threshold
- Per-element breakdown with velocity, ξ, Reynolds number, friction factor
- PDF report with pipeline elements table

### Pipe Wall Thickness Calculator
- Minimum required wall thickness per ASME B31.3 §304.1.2
- Pressure design thickness (Eq. 3a): t = PD / 2(SE + PY)
- 10 pipe materials: A106 A/B/C, A53 A/B, API 5L B/X42/X52, SS304L, SS316L
- Allowable stress S: linear interpolation from ASME Table A-1 across 15 temperature points (up to 565°C)
- 5 weld joint efficiency types: Seamless (E=1.0), ERW (0.85), LPG (0.6), FG (0.7), FBW (0.9)
- Y coefficient calculation per §304.1.1 for ferritic, austenitic, and other material types
- Corrosion allowance, NPT thread depth correction, and mill tolerance (default 12.5%)
- 23 NPS sizes (1/8″ to 24″) with ASME B36.10M schedule adequacy table
- Thin-wall condition check (t < D/6)
- PASS / FAIL status with recommended minimum schedule
- PDF report generation

### General
- Unified calculation history for all four calculator types, time-sorted
- Admin dashboard with compliance statistics
- Manual / Reference guide page
- SQLite persistence with SQLAlchemy ORM
- Responsive UI (works on desktop and tablet)

---

## 4. Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Browser                          │
│         Jinja2 HTML templates + vanilla JS              │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (form POST / fetch JSON)
┌────────────────────────▼────────────────────────────────┐
│                    Flask App  (app.py)                   │
│                                                         │
│  Routes:  /calculate  /cii  /egbp  /pipe  /report      │
│           /history  /admin  /manual                     │
│           /api/calculate-cii   /api/cii-report          │
│           /calculate-egbp      /api/egbp-report         │
│           /calculate-pipe      /api/pipe-report         │
└──────┬──────────────┬──────────────┬──────────────┬─────┘
       │              │              │              │
┌──────▼──────┐ ┌─────▼──────┐ ┌────▼──────┐ ┌────▼──────────┐
│  calculators│ │ calculators│ │calculators│ │  calculators  │
│  /eexi/     │ │  /cii/     │ │  /egbp/   │ │  /pipe_wall/  │
│ calculator  │ │ calculator │ │ calculator│ │  calculator   │
└──────┬──────┘ └────────────┘ └───────────┘ └───────────────┘
       │
  ┌────▼─────────────────────────────┐
  │  Sub-modules                     │
  │  emissions.py  — PME, PAE terms  │
  │  eexi_core.py  — attained/req'd  │
  │  epl.py        — MCRlim solver   │
  └──────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────┐
│                   database/db.py                        │
│  Vessel | CIICalculation | EGBPCalculation              │
│  PipeWallCalculation                                    │
│                SQLite  (instance/vessels.db)            │
└─────────────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────┐
│              reports/pdf_generator.py                   │
│   generate_pdf_report()       — EEXI                   │
│   generate_cii_pdf_report()   — CII                    │
│   generate_egbp_pdf_report()  — EGBP                   │
│   generate_pipe_pdf_report()  — Pipe Wall              │
│              (ReportLab)                                │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Technology Stack

| Layer | Technology | Version / Notes |
|---|---|---|
| Web Framework | Flask | 3.x |
| ORM / Database | Flask-SQLAlchemy + SQLite | 3.x |
| PDF Generation | ReportLab | 4.x |
| Templating | Jinja2 | (bundled with Flask) |
| Frontend JS | Vanilla JavaScript | ES6+ |
| Frontend CSS | Custom CSS | No framework |
| Python | CPython | 3.11+ |

---

## 6. Project Structure

```
eexi-calculator/
│
├── app.py                          # Flask application, all routes
│
├── calculators/                    # Core calculation engine
│   ├── __init__.py
│   ├── eexi/
│   │   ├── calculator.py           # EEXI orchestrator (main entry point)
│   │   ├── eexi_core.py            # Attained / Required EEXI formulas
│   │   ├── emissions.py            # PME, PAE, ME/AE emission terms
│   │   ├── epl.py                  # EPL / MCRlim iterative solver
│   │   └── __init__.py
│   ├── cii/
│   │   ├── calculator.py           # Full CII pipeline (attained, required, rating)
│   │   └── __init__.py
│   ├── egbp/
│   │   ├── calculator.py           # EGBP pressure loss pipeline
│   │   └── __init__.py
│   ├── pipe_wall/
│   │   ├── calculator.py           # ASME B31.3 pipe wall thickness calculator
│   │   └── __init__.py
│   └── utils/
│       ├── fuel_factors.py         # CF values per MARPOL Annex VI
│       ├── ship_params.py          # EEXI reference line params + reduction factors
│       └── validators.py           # Input validation
│
├── database/
│   └── db.py                       # SQLAlchemy models: Vessel, CIICalculation,
│                                   # EGBPCalculation, PipeWallCalculation
│
├── reports/
│   ├── pdf_generator.py            # ReportLab PDF builders for all 4 calculators
│   └── generated/                  # Auto-created; stores generated PDF files
│
├── templates/                      # Jinja2 HTML templates
│   ├── layout.html                 # Base layout with nav
│   ├── index.html                  # EEXI input form
│   ├── result.html                 # EEXI results page
│   ├── cii.html                    # CII input form + live results
│   ├── egbp.html                   # EGBP builder + live results
│   ├── pipe.html                   # Pipe wall input form + live results
│   ├── history.html                # Unified calculation history (all 4 types)
│   ├── admin.html                  # Admin statistics dashboard
│   └── manual.html                 # User reference guide
│
├── frontend/                       # React/Vite frontend (scaffold, in development)
│   ├── src/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json                # React 19.2, TypeScript 6.0, Vite 8.0
│   └── vite.config.ts
│
├── instance/
│   └── vessels.db                  # SQLite database (auto-created)
│
├── DEPLOYMENT_GUIDE.md
└── README.md
```

---

## 7. Calculators — Technical Detail

### 7.1 EEXI Calculator

**Regulatory basis:** IMO MEPC.350(78), MEPC.333(76)

#### Attained EEXI Formula

```
                  PME × CF_ME × SFC_ME  +  PAE × CF_AE × SFC_AE
Attained EEXI = ─────────────────────────────────────────────────────────────
                   f_i × f_c × f_l × Capacity × f_w × V_ref × f_m
```

Where:
- **PME** = 0.75 × MCR × f_eff  (main engine reference power, kW)
- **CF** = CO2 conversion factor (gCO2/gFuel) — per MARPOL Annex VI Reg. 2
- **SFC** = specific fuel consumption at 75% MCR (g/kWh)
- **PAE** = auxiliary engine power (kW); defaults to IMO formula if not entered:
  - MCR ≥ 10,000 kW → PAE = 0.025 × MCR + 250
  - MCR < 10,000 kW → PAE = 0.05 × MCR
- **Capacity** = DWT for most types; GT for Ro-Ro Passenger and Cruise; 0.70 × DWT for Container
- **V_ref** = design speed at 75% MCR (knots)
- **f_eff** = efficiency factor for shaft generators / WHR (0 < f_eff ≤ 1.0)
- **f_i** = capacity correction factor
- **f_w** = minimum propulsion power / weather correction
- **f_c** = cubic capacity correction
- **f_l** = general cargo factor
- **f_m** = ice-class correction

#### Required EEXI Formula

```
Required EEXI = a × DWT^(−c) × (1 − reduction_factor)
```

Reference line parameters (a, c) and reduction factors by ship type and size are sourced from IMO MEPC.350(78) Annex 9, Table 1.

#### CO2 Conversion Factors (CF)

| Fuel Type | CF (gCO2/gFuel) |
|---|---|
| HFO / RMG / RMK | 3.114 |
| MDO / MGO (DMA, DMB, DMZ) | 3.206 |
| LNG | 2.750 |
| Methanol | 1.375 |
| LPG Propane | 3.000 |
| LPG Butane | 3.030 |
| Ethane | 2.927 |

#### EEXI Reduction Factors by Ship Type and Size

| Ship Type | DWT / GT Range | Reduction |
|---|---|---|
| Bulk Carrier | ≥ 200,000 DWT | 15% |
| Bulk Carrier | 20,000–199,999 DWT | 20% |
| Tanker | ≥ 200,000 DWT | 15% |
| Tanker | 20,000–199,999 DWT | 20% |
| Container | ≥ 200,000 DWT | 50% |
| Container | 120,000–199,999 DWT | 45% |
| Container | 80,000–119,999 DWT | 35% |
| Container | 40,000–79,999 DWT | 30% |
| Container | 15,000–39,999 DWT | 20% |
| LNG Carrier | ≥ 10,000 DWT | 30% |
| Gas Carrier | ≥ 15,000 DWT | 30% |
| General Cargo | ≥ 15,000 DWT | 30% |

#### EPL / MCRlim — Iterative Solver

When a vessel is non-compliant, the tool calculates the Engine Power Limitation (EPL) required to achieve compliance. Because reducing power also reduces speed, which in turn changes the EEXI denominator, this requires an iterative solution:

```
Goal: find PME_lim such that Attained_EEXI(PME_lim, V_lim) = Required_EEXI

V_lim = V_ref × (PME_lim / PME_orig)^(1/n)

Each iteration:
  V_new  = V_ref × (PME_current / PME_orig)^(1/n)
  PME_new = (Required × Capacity × V_new × f_factors − AE_emissions) / (CF_ME × SFC_ME)

Converges after ~10–20 iterations.
```

Speed-power exponent **n** by ship type (from MEPC.333(76)):

| Ship Type | n |
|---|---|
| Bulk Carrier | 4.5 |
| Tanker | 6.5 (adjusted to 7.0315 for reference matching) |
| Container | 3.0 |
| General Cargo | 4.5 |
| LNG / Gas / Ro-Ro / Cruise | 3.0 |

**MCR_lim** = PME_lim / 0.83 (since PME is defined at 83% of MCR for EPL cases)

---

### 7.2 CII Calculator

**Regulatory basis:** IMO MEPC.352(78), MEPC.353(78), MEPC.354(78), MEPC.355(78)

#### Attained CII Formula

```
                 Σ (CF_j × (FC_j − deductions_j))
Attained CII = ─────────────────────────────────────────────
                      Capacity × (Distance − D_x)
```

Where:
- **FC_j** = annual fuel consumption per fuel type j (grams; input in metric tonnes, converted ×10⁶)
- **CF_j** = CO2 conversion factor for fuel j
- **Capacity** = DWT (most types) or GT (Ro-Ro passenger, Cruise)
- **Distance** = total distance sailed (nautical miles)
- **D_x** = voyage deduction distance (port calls where fuel was consumed without sailing)
- **Correction term** = (0.75 − 0.03 × yi) × (FC_electrical + FC_boiler + FC_others); yi = max(0, year − 2023)

#### Required CII Formula

```
Required CII = a × DWT^(−c) × (1 − dd/100)
```

CII reference line parameters (a, c) — MEPC.353(78):

| Ship Type | a | c | Capacity |
|---|---|---|---|
| Bulk Carrier | 4745.0 | 0.622 | DWT |
| Tanker | 5247.0 | 0.610 | DWT |
| Container | 1984.0 | 0.489 | DWT |
| General Cargo | 31948.0 | 0.792 | DWT |
| Ro-Ro Cargo | 10952.0 | 0.637 | DWT |
| Ro-Ro Passenger | 7540.0 | 0.587 | GT |
| LNG Carrier | 144050.0 | 0.865 | DWT |
| Gas Carrier | 8104.0 | 0.639 | DWT |
| Cruise | 930.0 | 0.383 | GT |

#### CII Reduction Factors (dd) by Year

| Year | dd (%) |
|---|---|
| 2023 | 5 |
| 2024 | 7 |
| 2025 | 9 |
| 2026 | 11 |
| 2027+ | 11 (under MEPC review) |

#### CII Rating Boundaries

Rating boundaries use ship-type specific d-vectors from MEPC.354(78):

```
A/B boundary = exp(d1) × Required CII
B/C boundary = exp(d2) × Required CII
C/D boundary = exp(d3) × Required CII   (d3 = 0.00 for all types → boundary = Required CII)
D/E boundary = exp(d4) × Required CII
```

| Ship Type | d1 | d2 | d3 | d4 |
|---|---|---|---|---|
| Bulk Carrier | −0.86 | −0.36 | 0.00 | 0.27 |
| Tanker | −0.72 | −0.29 | 0.00 | 0.20 |
| Container | −0.83 | −0.37 | 0.00 | 0.27 |
| General Cargo | −1.19 | −0.51 | 0.00 | 0.31 |
| LNG Carrier | −0.95 | −0.30 | 0.00 | 0.28 |

#### Tanker-Specific Corrections (MEPC.355(78))

| Correction | Formula |
|---|---|
| STS Tanker | AF = 6.1742 × DWT^(−0.246) |
| Shuttle Tanker | AF = 5.6805 × DWT^(−0.208) |
| Reefer (monitored) | FC = reefer_kWh × SFOC |
| Reefer (unmonitored) | FC = 2.75 × 24 × SFOC_avg × (days_sea + days_port) |

---

### 7.3 EGBP Calculator

**Regulatory basis / Technical reference:** Wärtsilä Engineering Document 18505-744-001

#### Pressure Loss Formula (Darcy-Weisbach)

```
ΔP = ξ × (½ × ρ × v²)

where:
  ρ = 353.05 / (T_K)            [exhaust gas density, kg/m³]
  v = Q / A = (ṁ/ρ) / A        [flow velocity, m/s]
  ξ = loss coefficient (element-specific)
```

#### Gas Properties

```
Density:      ρ = 353.05 / (T_C + 273.15)     [kg/m³]

Dynamic viscosity (Sutherland's law):
              μ = 1.458×10⁻⁶ × T_K^1.5 / (T_K + 110.4)

Kinematic viscosity:
              ν = μ / ρ                         [m²/s]
```

#### Friction Factor — Colebrook-White (iterative)

For turbulent flow (Re > 2300):
```
1/√λ = −2 × log₁₀(ε/D / 3.7 + 2.51 / (Re × √λ))

Solved iteratively (up to 100 iterations) until |λ_new − λ| < 10⁻¹⁰
For laminar flow (Re < 2300): λ = 64/Re
```

Straight pipe loss coefficient: `ξ_pipe = λ × (L/D)`

#### Element Loss Coefficients

| Element | ξ (or formula) |
|---|---|
| Straight Pipe | λ × L/D (Colebrook-White) |
| Pipe Bend | Lookup table, scaled by R/D ratio |
| Diffuser (expansion) | (1 − A₁/A₂)² — Borda-Carnot |
| Diffuser (contraction) | 0.5 × (1 − 1/(A₁/A₂)) — Weisbach |
| Orifice Plate | (1/(0.61 × β²))² − 1 |
| Butterfly Valve | 0.3319 |
| Gate Valve | 0.06928 |
| Swing Check Valve | 0.4777 |
| Lift Check Valve | 5.1821 |
| Globe Valve | 8.0 |
| Ball Valve | 0.05 |
| Silencer (35 dB(A)) | 2.35 |
| Boiler / Heat Recovery | 6.0 |
| Wye (through, 90°) | 0.17 |
| Wye (branch, 45°) | 0.20 |
| Outlet (atmospheric) | 1.0 |

#### Compliance Thresholds

| Status | Condition |
|---|---|
| PASSED | Total ΔP ≤ 85% of Max Allowable BP |
| BORDERLINE | 85% < Total ΔP ≤ Max Allowable BP |
| FAILED | Total ΔP > Max Allowable BP |

---

### 7.4 Pipe Wall Thickness Calculator

**Regulatory basis / Technical reference:** ASME B31.3 §304.1.2 (Process Piping Code)

#### Pressure Design Thickness — Equation 3a

```
         P × D_ext
t_dis = ─────────────────────
         2 × (S × E + P × Y)
```

Where:
- **P** = design gauge pressure (MPa)
- **D_ext** = pipe outside diameter (mm), per ASME B36.10M for standard NPS sizes
- **S** = allowable stress (MPa) — interpolated from ASME B31.3 Table A-1 based on material and temperature
- **E** = weld joint quality factor (1.0 for seamless, 0.85 for ERW, etc.)
- **Y** = temperature coefficient per §304.1.1 (0.4 below 482°C for ferritic; up to 0.7 for austenitic at high temp)

#### Required and Minimum Thickness

```
t_req = t_dis + CA + TD            (CA = corrosion allowance, TD = thread depth if threaded)
t_min = t_req × 100 / (100 − mill_tolerance)
```

#### Supported Materials

| Code | Description |
|---|---|
| A106A | A106 Grade A |
| A106B | A106 Grade B |
| A106C | A106 Grade C |
| A53A | A53 Grade A |
| A53B | A53 Grade B |
| API5LB | API 5L Grade B |
| API5LX42 | API 5L X42 |
| API5LX52 | API 5L X52 |
| SS304L | 304L Stainless Steel |
| SS316L | 316L Stainless Steel |

#### Weld Joint Efficiency Factors

| Code | Type | E Factor |
|---|---|---|
| S | Seamless | 1.0 |
| ERW | Electric Resistance Welded | 0.85 |
| FBW | Flash Butt Weld | 0.9 |
| FG | Furnace Butt Weld | 0.7 |
| LPG | Longitudinal PGW | 0.6 |

#### NPS Range and Schedule Adequacy

- Covers 23 NPS sizes: 1/8″ through 24″
- Checks each available ASME B36.10M schedule (5, 10, 40, 80, 120, 160, XXS) against t_min
- Returns the minimum adequate schedule and its actual wall thickness
- Includes thin-wall check: flags if t_dis < D_ext / 6 (thick-wall formula applies beyond this limit)

---

## 8. Database Schema

### `vessels` — EEXI Calculations

| Column | Type | Description |
|---|---|---|
| id | Integer PK | Auto-increment |
| name | String(100) | Vessel name (optional) |
| ship_type | String(50) | IMO ship type key |
| dwt | Float | Deadweight tonnage |
| gt | Float | Gross tonnage |
| mcr | Float | Main engine MCR (kW) |
| sfc | Float | ME specific fuel consumption (g/kWh) |
| fuel | String(20) | Main engine fuel type |
| speed | Float | Design speed V_ref (knots) |
| pae | Float | Auxiliary engine power (kW) |
| sfc_ae | Float | AE specific fuel consumption (g/kWh) |
| fuel_ae | String(20) | Auxiliary engine fuel type |
| f_eff | Float | Efficiency correction factor |
| f_i | Float | Capacity correction factor |
| f_w | Float | Weather correction factor |
| attained_eexi | Float | Calculated attained EEXI |
| required_eexi | Float | Calculated required EEXI |
| status | String(20) | `COMPLIANT` / `NON_COMPLIANT` |
| margin | Float | Compliance margin (%) |
| created_at | DateTime | UTC timestamp |
| user_local_time | String(50) | Browser local time (optional) |

### `cii_calculations` — CII Calculations

| Column | Type | Description |
|---|---|---|
| id | Integer PK | Auto-increment |
| ship_type | String(50) | IMO ship type key |
| year | Integer | Assessment year |
| attained_cii | Float | Calculated attained CII |
| required_cii | Float | Calculated required CII |
| rating | String(1) | A / B / C / D / E |
| margin_pct | Float | Margin vs required (%) |
| full_data | Text | Full result JSON (for PDF regeneration) |
| created_at | DateTime | UTC timestamp |

### `egbp_calculations` — EGBP Calculations

| Column | Type | Description |
|---|---|---|
| id | Integer PK | Auto-increment |
| mass_flow | Float | Exhaust gas mass flow (kg/s) |
| temperature | Float | Exhaust temperature (°C) |
| total_pa | Float | Total back pressure (Pa) |
| max_bp | Float | Maximum allowable back pressure (Pa) |
| status | String(20) | `PASSED` / `BORDERLINE` / `FAILED` |
| full_data | Text | Full result JSON (for PDF regeneration) |
| created_at | DateTime | UTC timestamp |

### `pipe_wall_calculations` — Pipe Wall Calculations

| Column | Type | Description |
|---|---|---|
| id | Integer PK | Auto-increment |
| nps | Float | Nominal pipe size |
| pressure_mpa | Float | Design gauge pressure (MPa) |
| temp_c | Float | Design temperature (°C) |
| material | String(20) | Material code (e.g. A106B) |
| weld_type | String(10) | Weld joint code (e.g. S, ERW) |
| corrosion_mm | Float | Corrosion allowance (mm) |
| threaded | Boolean | Whether NPT thread depth is applied |
| mill_tolerance | Float | Mill tolerance (%) |
| t_dis_mm | Float | Pressure design thickness (mm) |
| t_req_mm | Float | Required thickness incl. allowances (mm) |
| t_min_mm | Float | Minimum ordered thickness incl. mill tol. (mm) |
| S_mpa | Float | Allowable stress at design temperature (MPa) |
| dext_mm | Float | Pipe outside diameter (mm) |
| recommended_schedule | String(10) | Minimum adequate ASME schedule |
| available_thickness_mm | Float | Actual wall thickness of recommended schedule (mm) |
| status | String(20) | `PASS` / `FAIL` |
| full_data | Text | Full result JSON (for PDF regeneration) |
| created_at | DateTime | UTC timestamp |

---

## 9. API Reference

### EEXI

| Method | Route | Description |
|---|---|---|
| GET | `/` | EEXI calculator input form |
| POST | `/calculate` | Submit EEXI calculation, returns result page |
| GET | `/report/<vessel_id>` | Download EEXI PDF report for saved vessel |

### CII

| Method | Route | Description |
|---|---|---|
| GET | `/cii` | CII calculator page |
| POST | `/api/calculate-cii` | JSON API — calculate CII, save to DB, return JSON result |
| POST | `/api/cii-report` | JSON API — generate and download CII PDF |
| GET | `/cii-report-history/<calc_id>` | Download CII PDF for historical calculation |

**Request body for `/api/calculate-cii`:**
```json
{
  "ship_type": "tanker",
  "dwt": 75000,
  "gt": 0,
  "year": 2024,
  "distance_nm": 120000,
  "fc_hfo": 8500,
  "fc_mdo": 120,
  "voyage_hfo": 0,
  "voyage_distance": 0
}
```

**Response:**
```json
{
  "attained_cii": 3.4821,
  "required_cii": 4.0231,
  "capacity": 75000.0,
  "year": 2024,
  "distance_nm": 120000,
  "rating": {
    "rating": "B",
    "boundaries": {"A": 2.9041, "B": 3.6012, "C": 4.0231, "D": 4.8277},
    "margin_pct": 13.44,
    "description": "Minor superior — below required CII."
  },
  "corrections_applied": [],
  "reduction_factor_pct": 7
}
```

### EGBP

| Method | Route | Description |
|---|---|---|
| GET | `/egbp` | EGBP calculator page |
| POST | `/calculate-egbp` | JSON API — calculate EGBP, save to DB, return JSON result |
| POST | `/api/egbp-report` | JSON API — generate and download EGBP PDF |
| GET | `/egbp-report-history/<calc_id>` | Download EGBP PDF for historical calculation |

**Request body for `/calculate-egbp`:**
```json
{
  "mass_flow_kgs": 80.651,
  "temp_tc_c": 240.0,
  "max_bp_pa": 3000.0,
  "roughness_key": "steel_welded",
  "elements": [
    {"element_type": "pipe", "diameter_mm": 800, "length_mm": 15000},
    {"element_type": "pipe_bend", "diameter_mm": 800, "rd": 1.5, "angle_deg": 90},
    {"element_type": "silencer", "diameter_mm": 800},
    {"element_type": "outlet", "diameter_mm": 800}
  ]
}
```

### Pipe Wall Thickness

| Method | Route | Description |
|---|---|---|
| GET | `/pipe` | Pipe wall calculator page |
| POST | `/calculate-pipe` | JSON API — calculate pipe wall, save to DB, return JSON result |
| POST | `/api/pipe-report` | JSON API — generate and download pipe wall PDF |
| GET | `/pipe-report-history/<calc_id>` | Download pipe wall PDF for historical calculation |

**Request body for `/calculate-pipe`:**
```json
{
  "nps": 4.0,
  "pressure_mpa": 2.5,
  "temp_c": 120.0,
  "material": "A106B",
  "weld_type": "S",
  "corrosion_mm": 1.6,
  "threaded": false,
  "mill_tolerance": 12.5
}
```

**Response:**
```json
{
  "dext_mm": 114.3,
  "S_mpa": 137.9,
  "E_factor": 1.0,
  "Y_coeff": 0.4,
  "t_dis_mm": 1.028,
  "t_req_mm": 2.628,
  "t_min_mm": 3.004,
  "recommended_schedule": {"schedule": "40", "thickness_mm": 6.35, "adequate": true},
  "thin_wall_ok": true,
  "schedules": [...]
}
```

### General

| Method | Route | Description |
|---|---|---|
| GET | `/history` | Unified calculation history (all 4 calculator types) |
| GET | `/admin` | Admin dashboard with statistics |
| GET | `/manual` | User reference / manual page |

---

## 10. Installation & Setup

### Prerequisites

- Python 3.11 or higher
- pip

### Steps

```bash
# 1. Clone the repository
git clone <repository-url>
cd eexi-calculator

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# 3. Install dependencies
pip install flask flask-sqlalchemy reportlab

# 4. Run the application
python app.py
```

The app will be available at `http://127.0.0.1:5000`.

The SQLite database (`instance/vessels.db`) and the `reports/generated/` directory are created automatically on first run.

### Requirements Summary

```
flask
flask-sqlalchemy
reportlab
```

---

## 11. Running the Application

```bash
# Development mode (debug on, auto-reload)
python app.py

# Production (use a WSGI server)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

See `DEPLOYMENT_GUIDE.md` for cloud/production deployment instructions.

---

## 12. Regulatory References

| Document | Title | Applicability |
|---|---|---|
| IMO MEPC.350(78) | Guidelines on the method of calculation of the attained EEXI | EEXI formula, reference line, reduction factors |
| IMO MEPC.333(76) | Interim guidelines on the method of calculating the EEXI | EPL / MCRlim methodology |
| IMO MEPC.352(78) | 2022 Guidelines on operational CII and rating methodologies | CII rating (A–E) |
| IMO MEPC.353(78) | 2022 Guidelines on reference lines for CII | CII reference line (a, c parameters) |
| IMO MEPC.354(78) | 2022 Guidelines on rating boundaries | d-vector rating boundaries |
| IMO MEPC.355(78) | 2022 Guidelines on correction factors | Reefer, STS, shuttle tanker corrections |
| MARPOL Annex VI, Reg. 2 | CO2 conversion factors | CF values for all fuel types |
| Wärtsilä 18505-744-001 | Exhaust gas system design | EGBP element ξ values, methodology |
| ASME B31.3 | Process Piping Code — §304.1.2 | Pipe wall thickness formula |
| ASME B36.10M | Welded and Seamless Wrought Steel Pipe | Schedule thickness data |

---

## 13. Known Issues & Bug Fixes

### Bug 1 — Jinja2 TemplateSyntaxError in `cii.html` (Fixed)

**Error:** `jinja2.exceptions.TemplateSyntaxError: expected token 'end of statement block', got '='`

**Root cause:** The Jinja2 template tag `{% if y == "2024" %}` was corrupted — the `==` operator was split across multiple lines as `y=""` and `="2024"`, which Jinja2 cannot parse.

**Fix:** Consolidated the condition onto a single line:
```html
{% if y == "2024" %}selected{% endif %}
```

---

### Bug 2 — KeyError: 'compliant' in `pdf_generator.py` (Fixed)

**Error:** `KeyError: 'compliant'` when generating EEXI PDF report

**Root cause:** `pdf_generator.py` used `result_data['compliant']` (a boolean key that doesn't exist in the result dict). The EEXI calculator returns `result_data['status']` with string values `'COMPLIANT'` / `'NON_COMPLIANT'`.

**Fix:** Changed the check to:
```python
if result_data.get('status') == 'COMPLIANT':
```

---

### Bug 3 — TypeError: `<=` not supported between instances of `complex` and `int` in `epl.py` (Fixed)

**Error:** `TypeError: '<=' not supported between instances of 'complex' and 'int'` at `if max_pme <= 0`

**Root cause:** The EPL iterative solver drives `current_pme` negative when auxiliary engine emissions are large relative to the EEXI budget. On the next iteration, `(negative_number / p_me_original) ** (1/n)` — where `n` is a fractional exponent like `1/4.5` or `1/6.5` — produces a **Python complex number** rather than raising an error. This complex value silently propagated through the loop to `max_pme`, causing the `TypeError` when compared with `<= 0`.

**Fix:**
1. Check `current_pme <= 0` at the top of each iteration and break early (physically impossible state)
2. Use `float(current_pme)` after the loop to strip any residual complex leakage
3. Guard `new_v_ref` calculation against negative `max_pme`

```python
for _ in range(50):
    if current_pme <= 0 or p_me_original <= 0:
        current_pme = 0.0
        break
    current_v = v_ref * (current_pme / p_me_original) ** (1.0 / n)
    new_pme = (round(required_eexi, 2) * transport_work_base * current_v - ae_term) / (cf_me * sfc_me)
    current_pme = new_pme

max_pme = float(current_pme)
new_v_ref = v_ref * (max_pme / p_me_original) ** (1.0 / n) if (p_me_original > 0 and max_pme > 0) else v_ref
```

---

## 14. Future Roadmap

- **React frontend** — The `frontend/` directory contains a Vite + React 19 + TypeScript scaffold for a planned full SPA migration
- **User authentication** — Login system for multi-user environments (ship management companies)
- **Fleet management view** — Track compliance status across multiple vessels
- **CII trend projection** — Project future CII rating based on operational patterns
- **SEEMP integration** — Ship Energy Efficiency Management Plan document generation
- **Excel import** — Bulk upload vessel data from spreadsheets
- **Wind-assisted propulsion factor** — f_w correction for Flettner rotors and sails
- **API authentication** — API key or JWT for programmatic access
- **Docker deployment** — Containerised setup for easier cloud deployment
- **Pipe Wall enhancements** — Add ASME B31.1 Power Piping support; expand material database
