import datetime
import re
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from app.models import Property, Contact
from .llm_service import generate_comparison_summary, generate_personalized_recommendation

# --- STYLING CONSTANTS ---
styles = getSampleStyleSheet()
TITLE_STYLE = styles['h1']
HEADER_STYLE = styles['h2']
BODY_STYLE = styles['BodyText']
BRAND_COLOR = colors.HexColor("#00AEEF") # A modern blue
DARK_TEXT = colors.HexColor("#2C3E50")
LIGHT_TEXT = colors.HexColor("#FFFFFF")
GRID_COLOR = colors.HexColor("#BDC3C7")

# Create custom styles for formatted text
BOLD_STYLE = ParagraphStyle(
    'Bold',
    parent=BODY_STYLE,
    fontName='Helvetica-Bold',
    fontSize=10,
    spaceAfter=6,
)

BULLET_STYLE = ParagraphStyle(
    'Bullet',
    parent=BODY_STYLE,
    leftIndent=20,
    bulletIndent=10,
    fontSize=10,
    spaceAfter=4,
)

SUBHEADER_STYLE = ParagraphStyle(
    'SubHeader',
    parent=BODY_STYLE,
    fontName='Helvetica-Bold',
    fontSize=12,
    spaceAfter=8,
    spaceBefore=8,
)

def format_llm_text_for_pdf(text: str) -> list:
    """
    Convert markdown-formatted text from LLM to ReportLab paragraphs.
    
    Args:
        text: The raw text from LLM that may contain markdown
        
    Returns:
        List of ReportLab paragraph objects
    """
    paragraphs = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Handle markdown headers (e.g., "### Header" or "#### Header")
        if line.startswith('###'):
            header_text = line.lstrip('#').strip()
            paragraphs.append(Paragraph(header_text, SUBHEADER_STYLE))
            
        # Handle bold headers that are entire lines (e.g., **Header**)
        elif line.startswith('**') and line.endswith('**') and len(line) > 4:
            header_text = line[2:-2]  # Remove ** from both ends
            paragraphs.append(Paragraph(header_text, BOLD_STYLE))
            
        # Handle numbered lists (e.g., "1. Item")
        elif re.match(r'^\d+\.\s+', line):
            # Remove the number and format as bullet
            text_content = re.sub(r'^\d+\.\s+', '', line)
            # Also handle any ** bold formatting within the bullet point
            text_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text_content)
            paragraphs.append(Paragraph(f"• {text_content}", BULLET_STYLE))
            
        # Handle bullet points (e.g., "- Item")
        elif line.startswith('- '):
            text_content = line[2:]  # Remove "- "
            # Also handle any ** bold formatting within the bullet point
            text_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text_content)
            paragraphs.append(Paragraph(f"• {text_content}", BULLET_STYLE))
            
        # Handle regular paragraphs with inline bold formatting
        else:
            # Convert **text** to <b>text</b> for ReportLab
            formatted_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            paragraphs.append(Paragraph(formatted_line, BODY_STYLE))
    
    return paragraphs

def generate_comparison_pdf(p1: Property, p2: Property) -> bytes:
    """Generates a side-by-side comparison PDF for two properties."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    
    story = []

    # 1. Title
    story.append(Paragraph("Property Comparison", TITLE_STYLE))
    story.append(Spacer(1, 0.25 * inch))

    # 2. Comparison Table
    data = [
        ['Feature', f"Property #{p1.id}", f"Property #{p2.id}"],
        ['Address', Paragraph(p1.address, BODY_STYLE), Paragraph(p2.address, BODY_STYLE)],
        ['Price', f"{p1.price:,.0f} DZD", f"{p2.price:,.0f} DZD"],
        ['Area (sqm)', f"{p1.area_sqm} m²", f"{p2.area_sqm} m²"],
        ['Rooms', p1.number_of_rooms, p2.number_of_rooms],
        ['Type', p1.property_type.title(), p2.property_type.title()],
        ['Description', Paragraph(p1.description or "No description available", BODY_STYLE), Paragraph(p2.description or "No description available", BODY_STYLE)],
    ]

    table = Table(data, colWidths=[1.5*inch, 3*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), LIGHT_TEXT),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, GRID_COLOR),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(table)
    
    # 3. AI-Powered Comparison Summary
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("AI Analysis & Recommendation", HEADER_STYLE))
    story.append(Spacer(1, 0.1 * inch))
    
    # Generate LLM summary
    try:
        summary = generate_comparison_summary(p1, p2)
        # Format the summary text properly for PDF
        formatted_paragraphs = format_llm_text_for_pdf(summary)
        for para in formatted_paragraphs:
            story.append(para)
            story.append(Spacer(1, 0.05 * inch))
    except Exception as e:
        # Fallback if LLM service fails
        story.append(Paragraph("AI analysis temporarily unavailable. Please consult with your agent for detailed comparison insights.", BODY_STYLE))
    
    # 4. Footer
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Dar.ai", styles['Normal']))

    doc.build(story)
    return buffer.getvalue()

def generate_quote_pdf(prop: Property, contact: Contact) -> bytes:
    """Generates a formal quote PDF for a property and a contact."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    
    story = []

    # 1. Header with Company Info and Quote Title
    header_data = [
        [Paragraph("<b>Dar.ai Real Estate</b><br/>Your Trusted Partner in Real Estate", BODY_STYLE), Paragraph("<b>QUOTE</b>", TITLE_STYLE)],
    ]
    header_table = Table(header_data, colWidths=[4.5*inch, 3*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'), 
        ('ALIGN', (1, 0), (1, 0), 'RIGHT')
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.25 * inch))

    # 2. Client and Date Info
    today = datetime.date.today()
    info_data = [
        [Paragraph("<b>Quote For:</b>", BODY_STYLE), Paragraph(contact.name, BODY_STYLE)],
        [Paragraph("<b>Date:</b>", BODY_STYLE), Paragraph(today.strftime('%Y-%m-%d'), BODY_STYLE)],
        [Paragraph("<b>Valid Until:</b>", BODY_STYLE), Paragraph((today + datetime.timedelta(days=30)).strftime('%Y-%m-%d'), BODY_STYLE)],
    ]
    info_table = Table(info_data, colWidths=[1.5*inch, 6*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5 * inch))

    # 3. Property Details Section
    story.append(Paragraph("Property Details", HEADER_STYLE))
    story.append(Spacer(1, 0.1 * inch))
    
    property_details_data = [
        ['Property Information', 'Details'],
        [Paragraph("<b>Address:</b>", BODY_STYLE), Paragraph(prop.address, BODY_STYLE)],
        [Paragraph("<b>Property Type:</b>", BODY_STYLE), Paragraph(prop.property_type.title(), BODY_STYLE)],
        [Paragraph("<b>Area:</b>", BODY_STYLE), Paragraph(f"{prop.area_sqm} m²", BODY_STYLE)],
        [Paragraph("<b>Rooms:</b>", BODY_STYLE), Paragraph(str(prop.number_of_rooms), BODY_STYLE)],
        [Paragraph("<b>Description:</b>", BODY_STYLE), Paragraph(prop.description or "No description available", BODY_STYLE)],
    ]
    
    property_table = Table(property_details_data, colWidths=[2*inch, 5.5*inch])
    property_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), LIGHT_TEXT),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, GRID_COLOR),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(property_table)
    story.append(Spacer(1, 0.5 * inch))

    # 4. Pricing Section
    story.append(Paragraph("Pricing", HEADER_STYLE))
    story.append(Spacer(1, 0.1 * inch))
    
    line_items_data = [
        [Paragraph("<b>Item Description</b>", BODY_STYLE), Paragraph("<b>Price (DZD)</b>", BODY_STYLE)],
        [Paragraph(f"Real estate property located at: {prop.address}", BODY_STYLE), Paragraph(f"{prop.price:,.0f}", BODY_STYLE)],
        [Paragraph("", BODY_STYLE), Paragraph("", BODY_STYLE)], # Spacer row
        [Paragraph("<b>Total Amount</b>", BOLD_STYLE), Paragraph(f"<b>{prop.price:,.0f}</b>", BOLD_STYLE)],
    ]
    line_items_table = Table(line_items_data, colWidths=[5.5*inch, 2*inch])
    line_items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), LIGHT_TEXT),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, GRID_COLOR),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(line_items_table)
    story.append(Spacer(1, 1 * inch))

    # # 5. Footer
    # story.append(Paragraph("Thank you for your business!", SUBHEADER_STYLE))
    # story.append(Spacer(1, 0.1 * inch))
    # story.append(Paragraph("If you have any questions concerning this quote, please contact us at Dar.ai.", BODY_STYLE))
    # story.append(Spacer(1, 0.3 * inch))
    # story.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Dar.ai", styles['Normal']))

    doc.build(story)
    return buffer.getvalue()

def generate_personalized_recommendation_pdf(properties: list[Property], contact: Contact) -> bytes:
    """Generates a personalized property recommendation PDF based on contact preferences."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    
    story = []

    # 1. Title
    story.append(Paragraph(f"Personalized Property Recommendation for {contact.name}", TITLE_STYLE))
    story.append(Spacer(1, 0.25 * inch))

    # 2. Client Profile Section
    story.append(Paragraph("Client Profile & Preferences", HEADER_STYLE))
    story.append(Spacer(1, 0.1 * inch))
    
    # Client preferences table
    preferred_locations_str = ", ".join([loc.name for loc in contact.preferred_locations])
    property_types_str = ", ".join(contact.property_types)
    
    client_data = [
        ['Preference', 'Details'],
        ['Budget Range', f"{contact.min_budget:,.0f} - {contact.max_budget:,.0f} DZD"],
        ['Preferred Area', f"{contact.min_area_sqm} - {contact.max_area_sqm} m²"],
        ['Minimum Rooms', str(contact.min_rooms)],
        ['Property Types', property_types_str],
        ['Preferred Locations', preferred_locations_str],
    ]
    
    client_table = Table(client_data, colWidths=[2*inch, 5.5*inch])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), LIGHT_TEXT),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, GRID_COLOR),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(client_table)
    story.append(Spacer(1, 0.3 * inch))

    # 3. Properties Overview
    story.append(Paragraph("Properties Under Consideration", HEADER_STYLE))
    story.append(Spacer(1, 0.1 * inch))
    
    # Properties comparison table
    property_data = [['Property', 'Address', 'Price (DZD)', 'Area (m²)', 'Rooms', 'Type']]
    
    for i, prop in enumerate(properties, 1):
        # Check if property matches client preferences
        budget_match = contact.min_budget <= prop.price <= contact.max_budget
        area_match = contact.min_area_sqm <= prop.area_sqm <= contact.max_area_sqm
        rooms_match = prop.number_of_rooms >= contact.min_rooms
        type_match = prop.property_type in contact.property_types
        
        # Add visual indicators for matches
        price_str = f"{prop.price:,.0f}" + (" ✓" if budget_match else " ✗")
        area_str = f"{prop.area_sqm}" + (" ✓" if area_match else " ✗")
        rooms_str = f"{prop.number_of_rooms}" + (" ✓" if rooms_match else " ✗")
        type_str = prop.property_type.title() + (" ✓" if type_match else " ✗")
        
        property_data.append([
            f"Property {i}",
            Paragraph(prop.address, BODY_STYLE),
            price_str,
            area_str,
            rooms_str,
            type_str
        ])
    
    properties_table = Table(property_data, colWidths=[1*inch, 2.5*inch, 1.5*inch, 1*inch, 0.8*inch, 1.2*inch])
    properties_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BRAND_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), LIGHT_TEXT),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, GRID_COLOR),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    story.append(properties_table)
    story.append(Spacer(1, 0.1 * inch))
    
    # Legend
    story.append(Paragraph("✓ = Matches preference | ✗ = Does not match preference", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))

    # 4. AI-Powered Personalized Recommendation
    story.append(Paragraph("AI-Powered Personalized Analysis", HEADER_STYLE))
    story.append(Spacer(1, 0.1 * inch))
    
    # Generate LLM recommendation
    try:
        recommendation = generate_personalized_recommendation(properties, contact)
        # Format the recommendation text properly for PDF
        formatted_paragraphs = format_llm_text_for_pdf(recommendation)
        for para in formatted_paragraphs:
            story.append(para)
            story.append(Spacer(1, 0.05 * inch))
    except Exception as e:
        # Fallback if LLM service fails
        story.append(Paragraph("AI analysis temporarily unavailable. Please consult with your agent for detailed personalized recommendations.", BODY_STYLE))
    
    # 5. Footer
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by Dar.ai", styles['Normal']))

    doc.build(story)
    return buffer.getvalue()