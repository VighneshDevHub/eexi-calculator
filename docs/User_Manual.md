# EEXI Calculator - Professional User Manual & Technical Guide

## 📌 1. Introduction & Regulatory Context

The **Energy Efficiency Existing Ship Index (EEXI)** is a mandatory technical measure introduced by the **International Maritime Organization (IMO)** under the **MARPOL Annex VI** regulations (specifically MEPC.350(78)).

This tool is designed for ship owners, operators, and maritime consultants to:

- Assess vessel compliance with upcoming carbon intensity regulations.
- Calculate the technical efficiency of existing ships above 400 GT.
- Propose mitigation strategies like **Engine Power Limitation (EPL)** for non-compliant vessels.

---

## 🏗️ 2. Core Methodology & Formulae

### The Attained EEXI Formula

The calculator implements the standard IMO methodology:

$$Attained\ EEXI = \frac{(P_{ME} \times C_{F,ME} \times SFC_{ME}) + (P_{AE} \times C_{F,AE} \times SFC_{AE})}{\sum (f_i \times Capacity \times V_{ref} \times f_w)}$$

#### Key Components:

- **$P_{ME}$ (Main Engine Power)**: Calculated as 75% of the Maximum Continuous Rating (MCR).
- **$C_F$ (Carbon Factor)**: Conversion factor based on the fuel type (e.g., HFO = 3.114, MGO = 3.206).
- **$SFC$ (Specific Fuel Consumption)**: The certified fuel consumption at 75% MCR load.
- **$V_{ref}$ (Reference Speed)**: The vessel speed corresponding to $P_{ME}$ at the design draft.
- **$Capacity$**: Defined by ship type (DWT for most, 70% DWT for containers, GT for passenger ships).

### The Required EEXI (The Target)

The vessel's target is calculated using reference lines:
$$Required\ EEXI = a \times Capacity^{-c} \times (1 - \frac{X}{100})$$
Where **$a$** and **$c$** are IMO coefficients and **$X$** is the reduction factor (e.g., 20%).

---

## ⌨️ 3. Step-by-Step Operation Guide

### Step 1: Vessel Particulars

1. **Vessel Name**: For record-keeping and report generation.
2. **Ship Type**: **CRITICAL SELECTION**. This determines which IMO reference line coefficients ($a$, $c$) and reduction factors ($X$) are applied.
3. **DWT/GT**: Enter the vessel's deadweight or gross tonnage. The tool will automatically use the correct capacity unit for the selected ship type.

### Step 2: Engine Configuration

1. **MCR (kW)**: Enter the Total Maximum Continuous Rating.
2. **SFC (g/kWh)**: Enter the Specific Fuel Consumption at 75% load.
3. **Fuel Type**: Select the primary fuel. The tool applies the correct $C_F$ factor automatically.

### Step 3: Auxiliary Engine (AE)

- If specific AE data is unknown, the tool can estimate $P_{AE}$ based on the Main Engine MCR according to IMO default values ($P_{AE} = 0.05 \times MCR$).

### Step 4: Correction Factors

- **$f_{eff}$**: Account for energy-saving technologies (Waste Heat Recovery, etc.).
- **$f_i$**: Used for ice-classed vessels or specific design constraints.
- **$f_w$**: Weather factor (defaulted to 1.0 per EEXI standards).

---

## 📊 4. Interpreting Results & Compliance

### Visual Indicators

- 🟢 **COMPLIANT**: $Attained \le Required$. No technical modifications required.
- 🔴 **NON-COMPLIANT**: $Attained > Required$. Action is mandatory.

### Engine Power Limitation (EPL) Target

For non-compliant ships, the tool calculates the required **EPL**:

- **Limited MCR**: The maximum power level allowed to achieve compliance.
- **EPL Percentage**: The reduction required from original power (e.g., "Reduce MCR by 15%").

---

## 📂 5. Data Management & Reporting

- **PDF Generation**: Click "Generate Report" on the results page to create a formal document for class societies or internal audits.
- **History Log**: All calculations are saved locally. You can revisit, re-evaluate, or delete previous assessments.

---

## 🛠️ 6. Troubleshooting & FAQ

**Q: Why is my ship non-compliant despite being modern?**
A: EEXI is based on design parameters. High-speed vessels or those with oversized engines often face challenges.

**Q: What if I don't have the $V_{ref}$?**
A: Check the Sea Trial reports or the EEDI technical file. Accurate speed data is vital for a valid EEXI.

**Q: Is the data shared with the IMO?**
A: No. This tool is for local assessment. Your data remains on this server.

---

_Developed by Goltens Engineering - Leading Global Maritime Solutions._
