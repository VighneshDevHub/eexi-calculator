# EEXI Calculator - User Manual & Technical Guide

## 📌 Introduction
This manual provides a detailed guide on how to use the EEXI Calculator, explains the underlying maritime regulations, and details the calculation methodology used to ensure compliance with **IMO MARPOL Annex VI**.

---

## 🏗️ Core Concepts & Regulatory Framework

### What is EEXI?
The **Energy Efficiency Existing Ship Index (EEXI)** is a technical measure applicable to existing ships above 400 GT. It indicates the vessel's energy efficiency compared to a baseline. Ships must have an **Attained EEXI** equal to or less than the **Required EEXI**.

### The Mathematical Model
The application uses the standard IMO formula to calculate the CO2 emissions per unit of transport work:

1. **Main Engine Power ($P_{ME}$)**:
   - $P_{ME} = 0.75 \times MCR$
   - This represents the power at which the vessel is expected to operate during a typical voyage.

2. **Capacity**:
   - For most ships: **Deadweight (DWT)**.
   - For Container ships: **70% of DWT**.
   - For Cruise/Passenger ships: **Gross Tonnage (GT)**.

3. **Required EEXI**:
   - Calculated using reference line parameters ($a$ and $c$) specific to each ship type.
   - $Required = a \times Capacity^{-c} \times (1 - Reduction\%)$.

---

## ⌨️ How to Use the Calculator

### Step 1: Vessel Particulars
- **Vessel Name**: Enter for report identification.
- **Ship Type**: Critical selection as it defines the reference line coefficients ($a$, $c$) and reduction factors ($X$).
- **DWT/GT**: Enter the vessel's size. The tool will automatically use the correct unit for the reference line based on the ship type.

### Step 2: Main Engine (ME) Data
- **MCR (kW)**: Maximum Continuous Rating from the engine's technical file.
- **SFC (g/kWh)**: Specific Fuel Consumption at 75% MCR.
- **Fuel Type**: Selection defines the $C_F$ (Carbon Factor) constant.

### Step 3: Auxiliary Engine (AE) Data
- **Power (kW)**: Total rated power of auxiliary engines.
- **SFC (g/kWh)**: Specific Fuel Consumption of the auxiliary engines.
- **Fuel Type**: Can be different from the main engine.

### Step 4: Correction Factors (Advanced)
- **$f_{eff}$**: Efficiency factor for energy-saving devices (e.g., shaft generators).
- **$f_i$**: Capacity correction factor for ice-classed or specific designs.
- **$f_w$**: Weather correction factor (standardized at 1.0 for EEXI).

---

## 📊 Understanding the Results

### Compliance Statuses
- 🟢 **COMPLIANT**: Your vessel meets the IMO requirements. The margin shows the "headroom" available.
- 🟡 **BORDERLINE**: The vessel is compliant but within a 5% margin. It is recommended to consider efficiency improvements.
- 🔴 **NON-COMPLIANT**: The vessel fails to meet the requirement. Technical measures like **EPL** are required.

### Engine Power Limitation (EPL) Recommendation
If non-compliant, the tool provides:
1. **Limited MCR**: The maximum MCR the engine should be limited to.
2. **EPL %**: The percentage of the original MCR that can be utilized.
3. **Max PME**: The maximum allowable power at the EEXI reference condition.

---

## 📂 Report & History Management
- **Download PDF**: Generates a professional report containing all inputs, intermediate calculation steps, and the final verdict.
- **History**: Access previous calculations sorted by date. The system stores your local timezone to ensure timestamps are accurate to your location.

---
## 🛠️ Troubleshooting
- **Missing Input**: Ensure all fields marked with `*` or in the main sections are filled.
- **Invalid Unit**: Ensure power is in kW and speed is in knots.
- **Calculation Error**: Verify that $V_{ref}$ is positive and within a realistic range for the ship type.

---
*Goltens EEXI Compliance Tool - Empowering Sustainable Shipping.*
