# EEXI Calculator - User Manual

## Introduction
This manual provides instructions on how to use the EEXI Calculator to assess ship compliance with IMO Energy Efficiency Existing Ship Index (EEXI) regulations.

## Getting Started
1. Open the application in your web browser (default: `http://localhost:5000`).
2. You will be presented with the **Vessel Particulars** form.

## Step-by-Step Instructions

### 1. Enter Basic Information
- **Vessel Name**: Enter the name of the ship for identification.
- **Ship Type**: Select the appropriate category from the dropdown (e.g., Bulk Carrier, Tanker, Container Ship). This selection determines the reference line parameters used.
- **Deadweight (DWT)**: Enter the deadweight in tonnes. Required for most ship types.
- **Gross Tonnage (GT)**: Enter the gross tonnage. Required for Ro-Ro passenger and Cruise ships.

### 2. Enter Main Engine (ME) Data
- **Main Engine MCR**: Enter the Maximum Continuous Rating of the main engine in kW.
- **ME SFC**: Enter the Specific Fuel Consumption at 75% MCR in g/kWh (from the NOx Technical File).
- **Fuel Type**: Select the fuel used by the main engine. This determines the CO2 conversion factor (CF).
- **Design Speed (V_ref)**: Enter the vessel's design speed at 75% MCR in knots.

### 3. Enter Auxiliary Engine (AE) Data (Optional)
- **AE Rated Power**: Total rated power of auxiliary engines in kW.
- **AE SFC**: Specific Fuel Consumption of auxiliary engines.
- **AE Fuel Type**: Select if different from the main engine.

### 4. Correction Factors
- Default values are set to **1.0**. Only change these if you have specific efficiency data (e.g., shaft generators, waste-heat recovery) or specific correction factors as per MEPC.351(78).

### 5. Calculate & Review Results
- Click **"Calculate EEXI Compliance"**.
- The **Results Page** will display:
    - **Attained EEXI**: Your vessel's calculated index.
    - **Required EEXI**: The maximum index allowed for your ship type and size.
    - **Status**:
        - <span style="color: green;">**COMPLIANT**</span>: Attained <= Required.
        - <span style="color: orange;">**BORDERLINE**</span>: Within 5% of the limit.
        - <span style="color: red;">**NON-COMPLIANT**</span>: Attained > Required.
    - **EPL Recommendation**: If non-compliant, the tool provides the required MCR limit to achieve compliance.

### 6. Generate Report
- Click **"Download PDF Report"** to save a detailed summary of the calculation.

### 7. History
- Click **"History"** in the navigation bar to view and download reports from previous assessments.

## Troubleshooting
- **Missing Fields**: Ensure all required fields (marked or in the main sections) are filled.
- **Invalid Input**: Ensure only positive numbers are entered for power, speed, and consumption.
- **Capacity Error**: If you select a ship type that requires DWT but only provide GT (or vice versa), the tool will prompt you for the correct input.
