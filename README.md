# Web-Based EEXI Calculator for Existing Ships

## 🚢 Project Overview

This project is a professional-grade maritime compliance tool developed to calculate the **Energy Efficiency Existing Ship Index (EEXI)**. It is designed to assist ship owners, operators, and naval architects in determining if a vessel meets the stringent carbon intensity regulations set by the **International Maritime Organization (IMO)** under MARPOL Annex VI.

The calculator provides a complete end-to-end workflow: from technical data input to compliance verification, and finally, generating an Engine Power Limitation (EPL) recommendation for non-compliant vessels.

---

## 📐 Mathematical Model & Core Concepts

### 1. Attained EEXI Formula

The core calculation follows **IMO Resolution MEPC.350(78)**. The attained EEXI represents the specific CO2 emissions of a ship, normalized by its transport work.

$$Attained\ EEXI = \frac{P_{ME} \cdot C_{F,ME} \cdot SFC_{ME} + P_{AE} \cdot C_{F,AE} \cdot SFC_{AE}}{f_i \cdot Capacity \cdot V_{ref} \cdot f_w}$$

#### Key Parameters:

- **$P_{ME}$ (Main Engine Power)**: Calculated as 75% of the Maximum Continuous Rating (MCR).
- **$C_F$ (Carbon Factor)**: Dimensionless conversion factor based on fuel type (e.g., HFO = 3.114, MDO = 3.206).
- **$SFC$ (Specific Fuel Consumption)**: Certified fuel consumption rate at 75% MCR.
- **$V_{ref}$ (Design Speed)**: The vessel's speed at the EEXI draught and 75% MCR.
- **$f_i, f_w$**: Correction factors for capacity and weather.

### 2. Required EEXI (Reference Line)

To be compliant, a ship's **Attained EEXI** must be less than or equal to its **Required EEXI**. The required value is derived from the EEDI reference lines with a specific reduction factor ($X$).

$$Required\ EEXI = a \cdot Capacity^{-c} \cdot (1 - \frac{X}{100})$$

Where:

- **$a$ and $c$**: Coefficients specific to the ship type (e.g., Bulk Carrier: $a=961.79, c=0.477$).
- **$X$**: The required reduction percentage (typically 5% to 10% for EEXI Phase 1).

### 3. Engine Power Limitation (EPL)

If a vessel is non-compliant, the tool derives the maximum allowable power to meet the target.
$$Max\ P_{ME} = \frac{Required\ EEXI \cdot Denominator - AE\ Term}{C_{F,ME} \cdot SFC_{ME}}$$
$$Limited\ MCR = \frac{Max\ P_{ME}}{0.75}$$

---

## 🛠️ Technical Architecture

- **Backend**: Python 3.12 with **Flask** framework for robust API and routing logic.
- **Database**: **SQLite** with **SQLAlchemy ORM** for persistent storage of calculation history and vessel data.
- **Frontend**: Responsive **HTML5**, **CSS3** (custom variables, grid layouts), and **JavaScript** for dynamic timezone detection and UI interactions.
- **PDF Engine**: **ReportLab** for generating professional, high-fidelity compliance reports.
- **Data Logic**: Modular Python structure for separation of concerns (emissions, ship parameters, validators, and core EEXI logic).

---

## 🚀 Key Features

- **Multi-Ship Type Support**: Pre-configured parameters for Bulk Carriers, Tankers, Container Ships, Gas Carriers, LNG Carriers, Ro-Ro, and Cruise ships.
- **Dynamic Timezone Handling**: Automatically detects the user's local time for accurate report dating globally.
- **Automated Compliance Verdicts**:
  - ✅ **COMPLIANT**: Vessel meets the required standard.
  - ❌ **NON-COMPLIANT**: Vessel fails and requires technical intervention.
- **Professional PDF Export**: One-click generation of a detailed Technical Report.
- **History Management**: Securely store and review previous calculations in a searchable history log.

---

## 📥 Installation

1. **Clone the project**:
   ```bash
   git clone <repository-url>
   ```
2. **Setup Virtual Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run Application**:
   ```bash
   python app.py
   ```

---

## 📝 User Manual

For a detailed guide on how to use each feature and understand the inputs, please refer to the [USER_MANUAL.md](./USER_MANUAL.md) or visit the **User Manual** page directly within the application.

---

_Developed as part of an Internship Project focused on Maritime Digitalization and Green Shipping Compliance._
