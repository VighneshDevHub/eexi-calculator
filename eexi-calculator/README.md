# EEXI Calculator

A web-based tool for calculating the Energy Efficiency Existing Ship Index (EEXI) according to IMO MEPC.350(78) guidelines.

## Features

- **Attained EEXI Calculation**: Computes the actual EEXI based on vessel particulars, engine data, and fuel type.
- **Required EEXI Reference**: Automatically retrieves reference line coefficients (a, c) and reduction factors (X) for all major ship types.
- **Compliance Status**: Instantly determines if a vessel is COMPLIANT, BORDERLINE, or NON-COMPLIANT.
- **EPL Recommendation**: Provides precise Engine Power Limitation (EPL) targets if the vessel is non-compliant.
- **PDF Report Generation**: Generates detailed, professional compliance reports for record-keeping.
- **Calculation History**: Stores all previous assessments in a local database for easy retrieval.

## Mathematical Model

The calculator follows the step-by-step derivation defined in MEPC.350(78):

1.  **Attained EEXI** = `[P_ME * CF_ME * SFC_ME + P_AE * CF_AE * SFC_AE] / (Capacity * V_ref * f_i * f_w)`
2.  **Required EEXI** = `a * Capacity^(-c) * (1 - X/100)`
3.  **EPL Target** = Derived by solving for the maximum allowable `P_ME` to meet the `Required EEXI`.

## Technology Stack

- **Backend**: Python 3.12, Flask
- **Database**: SQLite with SQLAlchemy
- **Frontend**: HTML5, CSS3 (Inter font, FontAwesome icons)
- **PDF Generation**: ReportLab

## Installation & Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-repo/eexi-calculator.git
    cd eexi-calculator
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application**:
    ```bash
    python app.py
    ```
    Access the tool at `http://localhost:5000`.

## Directory Structure

- `eexi/`: Core calculation logic modules (emissions, ship parameters, EPL, etc.)
- `database/`: Database models and initialization.
- `reports/`: PDF generation logic and storage.
- `static/`: CSS and JavaScript assets.
- `templates/`: HTML templates (Flask/Jinja2).

## License

This project is developed for educational and professional maritime compliance purposes.
