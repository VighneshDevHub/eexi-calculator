# Maritime Compliance & Analysis Suite

A comprehensive engineering toolkit for maritime regulatory compliance, focusing on EEXI, CII, and Exhaust Gas Back Pressure (EGBP) analysis.

## 🚢 Features

### 1. EEXI Calculator (Energy Efficiency Existing Ship Index)
- Calculate attained EEXI based on IMO Resolution MEPC.350(78).
- Support for various ship types (Tankers, Bulk Carriers, Containers, etc.).
- Engine Power Limitation (EPL) recommendations for non-compliant vessels.
- PDF report generation with technical breakdown.

### 2. CII Analysis (Carbon Intensity Indicator)
- Annual operational efficiency rating (A-E).
- Calculation of Required vs. Attained CII.
- Support for various correction factors and exclusions.
- Visual rating indicator and compliance trends.

### 3. EGBP Calculator (Exhaust Gas Back Pressure)
- Dynamic pipeline system modeling.
- Darcy-Weisbach & Colebrook-White methodology for pressure loss.
- Comprehensive library of pipeline elements (bends, valves, silencers, etc.).
- Integrated Wärtsilä engineering standards.
- Detailed pressure drop breakdown and PDF reporting.

### 4. Fleet Management & History
- Unified dashboard for all calculations.
- Persistent database storage for historical assessments.
- Admin dashboard for fleet-wide compliance monitoring.
- Fully responsive design for Desktop, Tablet, and Mobile.

## 🛠️ Tech Stack
- **Backend**: Python / Flask
- **Database**: SQLite / SQLAlchemy
- **Frontend**: Modern CSS3 (CSS Variables, Grid, Flexbox), Vanilla JavaScript
- **Reporting**: ReportLab (PDF Generation)
- **Testing**: PyTest

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/maritime-suite.git
   cd maritime-suite
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database and run the app:
   ```bash
   python app.py
   ```
   The application will be available at `http://127.0.0.1:5000`.

## 📖 User Manual
Detailed instructions for each calculator can be found in the **User Manual** section within the application.

## ⚖️ License
This project is developed for Goltens Maritime Compliance. All rights reserved.
