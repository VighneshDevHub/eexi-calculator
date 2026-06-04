# 🚢 Goltens Maritime Compliance Tool

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/Compliance-IMO%20MEPC-green.svg)](https://www.imo.org/)

A professional, web-based assessment tool for calculating **EEXI** (Energy Efficiency Existing Ship Index) and **CII** (Carbon Intensity Indicator) in accordance with the latest **IMO MARPOL Annex VI** regulations.

---

## 🌟 Key Features

- **Dual Assessment Engine**: Complete support for both Technical (EEXI) and Operational (CII) compliance.
- **Automated Calculations**: Implements complex IMO formulas for various ship types including Bulk Carriers, Tankers, and Container Ships.
- **Smart Correction Factors**: Includes support for STS operations, shuttle tankers, and reefer electrical deductions per MEPC.355(78).
- **Engine Power Limitation (EPL)**: Proactive recommendations for non-compliant vessels to achieve target EEXI.
- **Professional PDF Reporting**: Generate high-fidelity technical reports with one click.
- **Responsive Dashboard**: Modern, professional UI that works seamlessly across desktop and mobile devices.

---

## 📐 Regulatory Standards

This tool is built strictly upon the following **IMO Resolutions**:
- **MEPC.350(78)**: EEXI Calculation Guidelines
- **MEPC.351(78)**: EEXI Survey and Certification
- **MEPC.352(78)**: Attained Annual CII Formula
- **MEPC.353(78)**: CII Reference Lines
- **MEPC.354(78)**: CII Rating Boundaries (A-E)
- **MEPC.355(78)**: CII Correction Factors and Voyage Adjustments

---

## 🛠️ Technical Stack

- **Backend**: Python 3.12, Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3 (Modern Grid/Flexbox), JavaScript (ES6+)
- **Database**: SQLite (Persistent storage for assessment history)
- **Reporting**: ReportLab (Professional PDF generation)
- **Styling**: Custom CSS with glassmorphism and responsive design principles

---

## 📥 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd eexi-calculator
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize and run**:
   ```bash
   python app.py
   ```
   The application will be available at `http://127.0.0.1:5000`

---

## 📖 Documentation

For a deep dive into the methodology and step-by-step usage, visit the **User Manual** page within the application or refer to the technical guides in the `docs/` folder.

---

_This project was developed to accelerate digitalization in maritime compliance and support the global transition toward Green Shipping._
