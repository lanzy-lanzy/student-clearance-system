from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_students_pdf(students, request=None):
    """
    Generate a PDF report of students
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.white,
        alignment=TA_LEFT
    )
    
    normal_style = styles["Normal"]
    
    # Content elements
    elements = []
    
    # Title
    title = Paragraph("Student Management Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.25*inch))
    
    # Table data
    data = [
        [
            Paragraph("ID", header_style),
            Paragraph("Student ID", header_style),
            Paragraph("Name", header_style),
            Paragraph("Email", header_style),
            Paragraph("Course", header_style),
            Paragraph("Year Level", header_style),
            Paragraph("Contact", header_style),
            Paragraph("Status", header_style),
            Paragraph("Residence", header_style)
        ]
    ]
    
    # Add student data
    for student in students:
        year_level_text = {
            1: "1st Year",
            2: "2nd Year",
            3: "3rd Year",
            4: "4th Year",
            5: "5th Year"
        }.get(student.year_level, f"{student.year_level} Year")
        
        status = "Approved" if student.is_approved else "Pending"
        residence = "Boarder" if student.is_boarder else "Non-Boarder"
        
        data.append([
            str(student.id),
            student.student_id,
            f"{student.user.first_name} {student.user.last_name}",
            student.user.email,
            student.course.name if student.course else "N/A",
            year_level_text,
            student.contact_number or "N/A",
            status,
            residence
        ])
    
    # Create the table
    table = Table(data, repeatRows=1)
    
    # Style the table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])
    
    # Add alternating row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            table_style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)
    
    table.setStyle(table_style)
    elements.append(table)
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf
