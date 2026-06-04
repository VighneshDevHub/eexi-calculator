import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from datetime import datetime

def generate_pdf_report(vessel_data, result_data):
    """
    Generates a PDF report for the EEXI calculation.
    """
    reports_dir = os.path.join(os.getcwd(), 'reports', 'generated')
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
        
    # Use user local time for filename if available
    time_for_filename = datetime.now().strftime('%Y%m%d_%H%M%S')
    if vessel_data.get('user_local_time'):
        try:
            # Try to sanitize the user local time for filename
            time_for_filename = vessel_data['user_local_time'].replace('-', '').replace(' ', '_').replace(':', '')
        except:
            pass

    filename = f"EEXI_Report_{vessel_data['id']}_{time_for_filename}.pdf"
    file_path = os.path.join(reports_dir, filename)
    
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
        spaceAfter=30
    )
    
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#0284c7'),
        spaceBefore=20,
        spaceAfter=10
    )

    elements = []
    
    # Title
    elements.append(Paragraph("EEXI Compliance Report", title_style))
    
    # Use stored local time if available
    report_date = vessel_data.get('user_local_time', vessel_data.get('created_at', 'N/A'))
    elements.append(Paragraph(f"Date: {report_date}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Vessel Details
    elements.append(Paragraph("Vessel Particulars", section_style))
    vessel_info = [
        ["Vessel Name", vessel_data.get('name', 'N/A')],
        ["Ship Type", vessel_data['ship_type'].replace('_', ' ').title()],
        ["Deadweight (DWT)", f"{vessel_data['dwt']} tonnes"],
        ["Gross Tonnage (GT)", f"{vessel_data['gt']}"],
        ["Main Engine MCR", f"{vessel_data['mcr']} kW"],
        ["ME SFC", f"{vessel_data['sfc']} g/kWh"],
        ["Fuel Type", vessel_data['fuel'].upper()],
        ["Design Speed (V_ref)", f"{vessel_data['speed']} knots"]
    ]
    
    if vessel_data.get('pae') and vessel_data['pae'] > 0:
        vessel_info.append(["Auxiliary Engine Power", f"{vessel_data['pae']} kW"])
        vessel_info.append(["Auxiliary SFC", f"{vessel_data['sfc_ae']} g/kWh"])
        vessel_info.append(["Auxiliary Fuel Type", vessel_data.get('fuel_ae', vessel_data['fuel']).upper()])

    vessel_info.append(["Efficiency Factor (f_eff)", f"{vessel_data.get('f_eff', 1.0)}"])
    vessel_info.append(["Capacity Factor (f_i)", f"{vessel_data.get('f_i', 1.0)}"])
    vessel_info.append(["Weather Factor (f_w)", f"{vessel_data.get('f_w', 1.0)}"])

    t1 = Table(vessel_info, colWidths=[200, 250])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t1)
    
    # Results
    elements.append(Paragraph("Calculation Results", section_style))
    status_color = colors.green
    if result_data['status'] == 'NON_COMPLIANT': status_color = colors.red
    
    results_info = [
        ["Attained EEXI", f"{result_data['attained_eexi']} gCO2/t·nm"],
        ["Required EEXI", f"{result_data['required_eexi']} gCO2/t·nm"],
        ["Compliance Status", Paragraph(f"<b>{result_data['status']}</b>", ParagraphStyle('Status', textColor=status_color))],
        ["Margin", f"{result_data['margin']}%"]
    ]
    t2 = Table(results_info, colWidths=[200, 250])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t2)
    
    # EPL / MCRlim
    if result_data.get('epl'):
        elements.append(Paragraph("EPL / MCRlim Recommendation", section_style))
        if result_data['epl'].get('epl_possible'):
            epl_info = [
                ["Calculated MCRlim", f"{result_data['epl']['limited_mcr']} kW"],
                ["Max PME (83% of MCRlim)", f"{result_data['epl']['max_pme']} kW"],
                ["Estimated Speed Vref,lim", f"{result_data['epl']['new_v_ref']} kn"]
            ]
            if result_data['compliant']:
                elements.append(Paragraph("The vessel is compliant. For reference, the MCRlim required to exactly match the target is shown below.", styles['Normal']))
            else:
                elements.append(Paragraph(result_data['epl']['note'], styles['Normal']))
                
            elements.append(Spacer(1, 10))
            t3 = Table(epl_info, colWidths=[200, 250])
            t3.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(t3)
        else:
            elements.append(Paragraph(result_data['epl']['note'], ParagraphStyle('Error', textColor=colors.red)))
    
    doc.build(elements)
    return file_path

def generate_cii_pdf_report(vessel_data, result_data):
    """
    Generates a PDF report for the CII calculation.
    """
    reports_dir = os.path.join(os.getcwd(), 'reports', 'generated')
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
        
    time_for_filename = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"CII_Report_{result_data['year']}_{time_for_filename}.pdf"
    file_path = os.path.join(reports_dir, filename)
    
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
        spaceAfter=30
    )
    
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#3b82f6'),
        spaceBefore=20,
        spaceAfter=10
    )

    elements = []
    
    # Title
    elements.append(Paragraph("CII Compliance Report", title_style))
    elements.append(Paragraph(f"Assessment Year: {result_data['year']}", styles['Normal']))
    elements.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Vessel & Operating Data
    elements.append(Paragraph("Vessel & Operating Data", section_style))
    vessel_info = [
        ["Ship Type", result_data['inputs_echo']['ship_type'].replace('_', ' ').title()],
        ["Deadweight (DWT)", f"{result_data['inputs_echo']['dwt']} tonnes"],
        ["Gross Tonnage (GT)", f"{result_data['inputs_echo']['gt']}"],
        ["Distance Sailed", f"{result_data['distance_nm']} nm"],
        ["Capacity (used for CII)", f"{result_data['capacity']}"]
    ]
    
    t1 = Table(vessel_info, colWidths=[200, 250])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t1)
    
    # Results
    elements.append(Paragraph("CII Calculation Results", section_style))
    rating = result_data['rating']['rating']
    rating_colors = {'A': colors.green, 'B': colors.lightgreen, 'C': colors.orange, 'D': colors.red, 'E': colors.darkred}
    
    results_info = [
        ["Attained CII", f"{result_data['attained_cii']} gCO2/t·nm"],
        ["Required CII", f"{result_data['required_cii']} gCO2/t·nm"],
        ["CII Rating", Paragraph(f"<b>{rating}</b>", ParagraphStyle('Rating', textColor=rating_colors.get(rating, colors.black), fontSize=14))],
        ["Margin vs Required", f"{result_data['rating']['margin_pct']}%"],
        ["Rating Description", result_data['rating']['description']]
    ]
    
    t2 = Table(results_info, colWidths=[200, 250])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, -1), (-1, -1), 'TOP'),
    ]))
    elements.append(t2)
    
    # Corrections
    if result_data.get('corrections_applied'):
        elements.append(Paragraph("Correction Factors Applied (MEPC.355(78))", section_style))
        for corr in result_data['corrections_applied']:
            elements.append(Paragraph(f"• {corr}", styles['Normal']))
            
    # Boundaries
    elements.append(Paragraph("Rating Boundaries", section_style))
    b = result_data['rating']['boundaries']
    bound_info = [
        ["A/B Boundary", f"{b['A']}"],
        ["B/C Boundary", f"{b['B']}"],
        ["C/D Boundary", f"{b['C']}"],
        ["D/E Boundary", f"{b['D']}"]
    ]
    t3 = Table(bound_info, colWidths=[200, 250])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t3)
    
    doc.build(elements)
    return file_path
