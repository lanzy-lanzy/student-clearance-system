from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

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

def generate_boarders_pdf(students, request=None, school_year=None, semester=None):
    """
    Generate a PDF report of boarders for a dormitory owner
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
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

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=12,
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
    title = Paragraph("Dormitory Boarders Report", title_style)
    elements.append(title)

    # Subtitle with school year and semester
    if school_year and semester:
        subtitle = Paragraph(f"School Year: {school_year} | Semester: {semester}", subtitle_style)
        elements.append(subtitle)

    # Current date
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", normal_style)
    elements.append(date_text)
    elements.append(Spacer(1, 0.25*inch))

    # Table data
    data = [
        [
            Paragraph("Student ID", header_style),
            Paragraph("Name", header_style),
            Paragraph("Course", header_style),
            Paragraph("Year Level", header_style),
            Paragraph("Contact Number", header_style)
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

        data.append([
            student.student_id,
            f"{student.user.first_name} {student.user.last_name}",
            student.course.name if student.course else "N/A",
            year_level_text,
            student.contact_number or "N/A"
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

    # Summary section
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(f"Total Boarders: {len(students)}", styles['Heading3']))

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf

def generate_clearance_report_pdf(clearance_requests, request=None, school_year=None, semester=None):
    """
    Generate a PDF report of clearance requests for a dormitory owner
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

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=12,
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
    title = Paragraph("Dormitory Clearance Report", title_style)
    elements.append(title)

    # Subtitle with school year and semester
    if school_year and semester:
        subtitle = Paragraph(f"School Year: {school_year} | Semester: {semester}", subtitle_style)
        elements.append(subtitle)

    # Current date
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", normal_style)
    elements.append(date_text)
    elements.append(Spacer(1, 0.25*inch))

    # Table data
    data = [
        [
            Paragraph("Student ID", header_style),
            Paragraph("Name", header_style),
            Paragraph("Request Date", header_style),
            Paragraph("Status", header_style),
            Paragraph("Reviewed Date", header_style),
            Paragraph("Reviewed By", header_style),
            Paragraph("Notes", header_style)
        ]
    ]

    # Count statistics
    pending_count = 0
    approved_count = 0
    denied_count = 0

    # Add clearance request data
    for request in clearance_requests:
        # Update statistics
        if request.status == 'pending':
            pending_count += 1
        elif request.status == 'approved':
            approved_count += 1
        elif request.status == 'denied':
            denied_count += 1

        # Format dates
        request_date = request.request_date.strftime('%Y-%m-%d') if request.request_date else 'N/A'
        reviewed_date = request.reviewed_date.strftime('%Y-%m-%d') if request.reviewed_date else 'N/A'

        # Format status with proper capitalization
        status = request.status.capitalize() if request.status else 'N/A'

        data.append([
            request.student.student_id,
            f"{request.student.user.first_name} {request.student.user.last_name}",
            request_date,
            status,
            reviewed_date,
            request.reviewed_by.get_full_name() if request.reviewed_by else 'N/A',
            request.notes or 'N/A'
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

    # Summary section
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Summary Statistics", styles['Heading3']))

    summary_data = [
        ["Total Requests", "Pending", "Approved", "Denied"],
        [str(len(clearance_requests)), str(pending_count), str(approved_count), str(denied_count)]
    ]

    summary_table = Table(summary_data)
    summary_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ])

    # Color the cells based on status
    summary_style.add('BACKGROUND', (1, 1), (1, 1), colors.yellow)
    summary_style.add('BACKGROUND', (2, 1), (2, 1), colors.lightgreen)
    summary_style.add('BACKGROUND', (3, 1), (3, 1), colors.lightcoral)

    summary_table.setStyle(summary_style)
    elements.append(summary_table)

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf
