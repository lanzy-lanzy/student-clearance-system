from io import BytesIO
from datetime import datetime
import os
from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, Flowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend

# Import semester choices from core.models
from core.models import SEMESTER_CHOICES

# Import common utilities from pdf_utils
from core.pdf_utils import PageNumberFooter, get_logo_path
from django.db.models import Count

# Define emerald theme colors
EMERALD_DARK = HexColor('#047857')  # Emerald-700
EMERALD_MEDIUM = HexColor('#10B981')  # Emerald-500
EMERALD_LIGHT = HexColor('#6EE7B7')  # Emerald-300
EMERALD_PALE = HexColor('#D1FAE5')  # Emerald-100
EMERALD_BG = HexColor('#ECFDF5')  # Emerald-50

# Define other colors for charts and tables
BLUE_MEDIUM = HexColor('#3B82F6')  # Blue-500
RED_MEDIUM = HexColor('#EF4444')  # Red-500
YELLOW_MEDIUM = HexColor('#F59E0B')  # Amber-500
GRAY_MEDIUM = HexColor('#6B7280')  # Gray-500

# Dormitory-specific PDF generation functions
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

# Office-specific PDF generation functions
def generate_office_clearance_report_pdf(clearance_requests, request=None, school_year=None, semester=None, office=None):
    """
    Generate a PDF report of clearance requests for a specific office
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
        spaceAfter=12,
        textColor=EMERALD_DARK
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=EMERALD_MEDIUM
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

    # Add logo if available
    logo_path = get_logo_path()
    if logo_path:
        img = Image(logo_path, width=1.5*inch, height=1.5*inch)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Spacer(1, 0.25*inch))

    # Title
    office_name = office.name if office else "Office"
    title = Paragraph(f"{office_name} Clearance Report", title_style)
    elements.append(title)

    # Subtitle with school year and semester
    if school_year and semester:
        semester_display = dict(SEMESTER_CHOICES).get(semester, semester)
        subtitle = Paragraph(f"School Year: {school_year} | Semester: {semester_display}", subtitle_style)
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
            request.student.course.name if request.student.course else "N/A",
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
        ('BACKGROUND', (0, 0), (-1, 0), EMERALD_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, EMERALD_MEDIUM),
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
            table_style.add('BACKGROUND', (0, i), (-1, i), EMERALD_PALE)

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
        ('BACKGROUND', (0, 0), (-1, 0), EMERALD_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, EMERALD_MEDIUM),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ])

    # Color the cells based on status
    summary_style.add('BACKGROUND', (1, 1), (1, 1), YELLOW_MEDIUM)
    summary_style.add('BACKGROUND', (2, 1), (2, 1), EMERALD_LIGHT)
    summary_style.add('BACKGROUND', (3, 1), (3, 1), RED_MEDIUM)

    summary_table.setStyle(summary_style)
    elements.append(summary_table)

    # Add page numbers
    elements.append(PageNumberFooter())

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf

def generate_student_performance_report_pdf(clearance_requests, request=None, school_year=None, semester=None, office=None):
    """
    Generate a PDF report of student performance for a specific office
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
        spaceAfter=12,
        textColor=EMERALD_DARK
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=EMERALD_MEDIUM
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

    # Add logo if available
    logo_path = get_logo_path()
    if logo_path:
        img = Image(logo_path, width=1.5*inch, height=1.5*inch)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Spacer(1, 0.25*inch))

    # Title
    office_name = office.name if office else "Office"
    title = Paragraph(f"{office_name} Student Performance Report", title_style)
    elements.append(title)

    # Subtitle with school year and semester
    if school_year and semester:
        semester_display = dict(SEMESTER_CHOICES).get(semester, semester)
        subtitle = Paragraph(f"School Year: {school_year} | Semester: {semester_display}", subtitle_style)
        elements.append(subtitle)

    # Current date
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", normal_style)
    elements.append(date_text)
    elements.append(Spacer(1, 0.25*inch))

    # Group by course
    course_data = {}
    for req in clearance_requests:
        course_name = req.student.course.name if req.student.course else "Unknown"
        if course_name not in course_data:
            course_data[course_name] = {
                'total': 0,
                'approved': 0,
                'denied': 0,
                'pending': 0
            }

        course_data[course_name]['total'] += 1
        if req.status == 'approved':
            course_data[course_name]['approved'] += 1
        elif req.status == 'denied':
            course_data[course_name]['denied'] += 1
        else:
            course_data[course_name]['pending'] += 1

    # Course performance table
    elements.append(Paragraph("Performance by Course", styles['Heading3']))

    course_table_data = [
        [
            Paragraph("Course", header_style),
            Paragraph("Total Requests", header_style),
            Paragraph("Approved", header_style),
            Paragraph("Denied", header_style),
            Paragraph("Pending", header_style),
            Paragraph("Approval Rate", header_style)
        ]
    ]

    # Sort courses by name
    sorted_courses = sorted(course_data.items())

    for course_name, stats in sorted_courses:
        approval_rate = (stats['approved'] / stats['total'] * 100) if stats['total'] > 0 else 0
        course_table_data.append([
            course_name,
            str(stats['total']),
            str(stats['approved']),
            str(stats['denied']),
            str(stats['pending']),
            f"{approval_rate:.1f}%"
        ])

    # Add a total row
    total_requests = sum(stats['total'] for _, stats in sorted_courses)
    total_approved = sum(stats['approved'] for _, stats in sorted_courses)
    total_denied = sum(stats['denied'] for _, stats in sorted_courses)
    total_pending = sum(stats['pending'] for _, stats in sorted_courses)
    total_approval_rate = (total_approved / total_requests * 100) if total_requests > 0 else 0

    course_table_data.append([
        "TOTAL",
        str(total_requests),
        str(total_approved),
        str(total_denied),
        str(total_pending),
        f"{total_approval_rate:.1f}%"
    ])

    course_table = Table(course_table_data, repeatRows=1)
    course_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), EMERALD_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), EMERALD_PALE),  # Total row
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, EMERALD_MEDIUM),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])

    # Add alternating row colors
    for i in range(1, len(course_table_data)-1):  # Skip the header and total rows
        if i % 2 == 0:
            course_table_style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)

    course_table.setStyle(course_table_style)
    elements.append(course_table)
    elements.append(Spacer(1, 0.5*inch))

    # Add page numbers
    elements.append(PageNumberFooter())

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf

def generate_processing_time_report_pdf(clearance_requests, request=None, school_year=None, semester=None, office=None):
    """
    Generate a PDF report of clearance request processing times for a specific office
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
        spaceAfter=12,
        textColor=EMERALD_DARK
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=EMERALD_MEDIUM
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

    # Add logo if available
    logo_path = get_logo_path()
    if logo_path:
        img = Image(logo_path, width=1.5*inch, height=1.5*inch)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Spacer(1, 0.25*inch))

    # Title
    office_name = office.name if office else "Office"
    title = Paragraph(f"{office_name} Processing Time Report", title_style)
    elements.append(title)

    # Subtitle with school year and semester
    if school_year and semester:
        semester_display = dict(SEMESTER_CHOICES).get(semester, semester)
        subtitle = Paragraph(f"School Year: {school_year} | Semester: {semester_display}", subtitle_style)
        elements.append(subtitle)

    # Current date
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", normal_style)
    elements.append(date_text)
    elements.append(Spacer(1, 0.25*inch))

    # Calculate processing times
    processing_times = []
    for req in clearance_requests:
        if req.request_date and req.reviewed_date:
            # Calculate processing time in days
            time_diff = req.reviewed_date - req.request_date
            days = time_diff.days
            processing_times.append((req, days))

    # Sort by processing time (ascending)
    processing_times.sort(key=lambda x: x[1])

    # Table data
    data = [
        [
            Paragraph("Student ID", header_style),
            Paragraph("Name", header_style),
            Paragraph("Request Date", header_style),
            Paragraph("Reviewed Date", header_style),
            Paragraph("Processing Time (Days)", header_style),
            Paragraph("Status", header_style)
        ]
    ]

    # Add request data
    for req, days in processing_times:
        request_date = req.request_date.strftime('%Y-%m-%d') if req.request_date else 'N/A'
        reviewed_date = req.reviewed_date.strftime('%Y-%m-%d') if req.reviewed_date else 'N/A'
        status = req.status.capitalize() if req.status else 'N/A'

        data.append([
            req.student.student_id,
            f"{req.student.user.first_name} {req.student.user.last_name}",
            request_date,
            reviewed_date,
            str(days),
            status
        ])

    # Create the table
    table = Table(data, repeatRows=1)

    # Style the table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), EMERALD_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, EMERALD_MEDIUM),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Center-align the days column
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])

    # Add alternating row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            table_style.add('BACKGROUND', (0, i), (-1, i), EMERALD_PALE)

    # Highlight long processing times (more than 7 days)
    for i in range(1, len(data)):
        try:
            days = int(data[i][4])
            if days > 7:
                table_style.add('BACKGROUND', (4, i), (4, i), RED_MEDIUM)
                table_style.add('TEXTCOLOR', (4, i), (4, i), colors.white)
            elif days <= 1:
                table_style.add('BACKGROUND', (4, i), (4, i), EMERALD_LIGHT)
        except ValueError:
            pass

    table.setStyle(table_style)
    elements.append(table)

    # Summary section
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Processing Time Statistics", styles['Heading3']))

    if processing_times:
        # Calculate statistics
        total_days = sum(days for _, days in processing_times)
        avg_days = total_days / len(processing_times)
        max_days = max(days for _, days in processing_times)
        min_days = min(days for _, days in processing_times)

        # Count requests by processing time range
        same_day = sum(1 for _, days in processing_times if days == 0)
        one_day = sum(1 for _, days in processing_times if days == 1)
        two_to_three = sum(1 for _, days in processing_times if 2 <= days <= 3)
        four_to_seven = sum(1 for _, days in processing_times if 4 <= days <= 7)
        more_than_seven = sum(1 for _, days in processing_times if days > 7)

        summary_data = [
            ["Metric", "Value"],
            ["Total Processed Requests", str(len(processing_times))],
            ["Average Processing Time", f"{avg_days:.1f} days"],
            ["Minimum Processing Time", f"{min_days} days"],
            ["Maximum Processing Time", f"{max_days} days"],
            ["Same Day Processing", f"{same_day} ({same_day/len(processing_times)*100:.1f}%)"],
            ["One Day Processing", f"{one_day} ({one_day/len(processing_times)*100:.1f}%)"],
            ["2-3 Days Processing", f"{two_to_three} ({two_to_three/len(processing_times)*100:.1f}%)"],
            ["4-7 Days Processing", f"{four_to_seven} ({four_to_seven/len(processing_times)*100:.1f}%)"],
            ["More than 7 Days", f"{more_than_seven} ({more_than_seven/len(processing_times)*100:.1f}%)"]
        ]

        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_style = TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), EMERALD_DARK),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (1, -1), 1, EMERALD_MEDIUM),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (1, -1), 10),
            ('TOPPADDING', (0, 1), (1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (1, -1), 6),
            ('BACKGROUND', (0, 1), (0, 4), EMERALD_PALE),
        ])

        # Highlight the rows with processing time ranges
        summary_style.add('BACKGROUND', (0, 5), (0, 9), colors.lightgrey)

        summary_table.setStyle(summary_style)
        elements.append(summary_table)
    else:
        elements.append(Paragraph("No processing time data available.", normal_style))

    # Add page numbers
    elements.append(PageNumberFooter())

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf

def generate_denial_reasons_report_pdf(clearance_requests, request=None, school_year=None, semester=None, office=None):
    """
    Generate a PDF report of denial reasons for a specific office
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
        spaceAfter=12,
        textColor=EMERALD_DARK
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=EMERALD_MEDIUM
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

    # Add logo if available
    logo_path = get_logo_path()
    if logo_path:
        img = Image(logo_path, width=1.5*inch, height=1.5*inch)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Spacer(1, 0.25*inch))

    # Title
    office_name = office.name if office else "Office"
    title = Paragraph(f"{office_name} Denial Reasons Report", title_style)
    elements.append(title)

    # Subtitle with school year and semester
    if school_year and semester:
        semester_display = dict(SEMESTER_CHOICES).get(semester, semester)
        subtitle = Paragraph(f"School Year: {school_year} | Semester: {semester_display}", subtitle_style)
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
            Paragraph("Request Date", header_style),
            Paragraph("Reviewed Date", header_style),
            Paragraph("Reviewed By", header_style),
            Paragraph("Denial Reason", header_style)
        ]
    ]

    # Add request data
    for req in clearance_requests:
        request_date = req.request_date.strftime('%Y-%m-%d') if req.request_date else 'N/A'
        reviewed_date = req.reviewed_date.strftime('%Y-%m-%d') if req.reviewed_date else 'N/A'

        data.append([
            req.student.student_id,
            f"{req.student.user.first_name} {req.student.user.last_name}",
            req.student.course.name if req.student.course else "N/A",
            request_date,
            reviewed_date,
            req.reviewed_by.get_full_name() if req.reviewed_by else 'N/A',
            req.notes or 'No reason provided'
        ])

    # Create the table
    table = Table(data, repeatRows=1)

    # Style the table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), EMERALD_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, EMERALD_MEDIUM),
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
            table_style.add('BACKGROUND', (0, i), (-1, i), EMERALD_PALE)

    table.setStyle(table_style)
    elements.append(table)

    # Summary section
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Common Denial Reasons", styles['Heading3']))

    # Analyze common reasons
    reason_counts = {}
    for req in clearance_requests:
        reason = req.notes or 'No reason provided'
        if reason not in reason_counts:
            reason_counts[reason] = 0
        reason_counts[reason] += 1

    if reason_counts:
        # Sort reasons by frequency (descending)
        sorted_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)

        reason_data = [
            [
                Paragraph("Denial Reason", header_style),
                Paragraph("Frequency", header_style),
                Paragraph("Percentage", header_style)
            ]
        ]

        for reason, count in sorted_reasons:
            percentage = (count / len(clearance_requests)) * 100
            reason_data.append([
                reason,
                str(count),
                f"{percentage:.1f}%"
            ])

        reason_table = Table(reason_data, colWidths=[5*inch, 1*inch, 1.5*inch], repeatRows=1)
        reason_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), EMERALD_DARK),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, EMERALD_MEDIUM),
            ('ALIGN', (1, 1), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ])

        # Add alternating row colors
        for i in range(1, len(reason_data)):
            if i % 2 == 0:
                reason_style.add('BACKGROUND', (0, i), (-1, i), EMERALD_PALE)

        reason_table.setStyle(reason_style)
        elements.append(reason_table)
    else:
        elements.append(Paragraph("No denial reasons data available.", normal_style))

    # Add page numbers
    elements.append(PageNumberFooter())

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf

def generate_department_report_pdf(clearance_requests, request=None, school_year=None, semester=None, office=None, department_id=None):
    """
    Generate a PDF report of clearance requests by academic department
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
        spaceAfter=12,
        textColor=EMERALD_DARK
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=EMERALD_MEDIUM
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

    # Add logo if available
    logo_path = get_logo_path()
    if logo_path:
        img = Image(logo_path, width=1.5*inch, height=1.5*inch)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Spacer(1, 0.25*inch))

    # Title
    office_name = office.name if office else "Office"

    # If a specific department is selected, include it in the title
    if department_id:
        from core.models import Dean
        try:
            department = Dean.objects.get(id=department_id)
            title = Paragraph(f"{office_name} Department Report - {department.name}", title_style)
        except Dean.DoesNotExist:
            title = Paragraph(f"{office_name} Department Report", title_style)
    else:
        title = Paragraph(f"{office_name} Department Report - All Departments", title_style)

    elements.append(title)

    # Subtitle with school year and semester
    if school_year and semester:
        semester_display = dict(SEMESTER_CHOICES).get(semester, semester)
        subtitle = Paragraph(f"School Year: {school_year} | Semester: {semester_display}", subtitle_style)
        elements.append(subtitle)

    # Current date
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", normal_style)
    elements.append(date_text)
    elements.append(Spacer(1, 0.25*inch))

    # Group data by department
    department_data = {}

    for req in clearance_requests:
        # Get department name from the student's course
        department_name = req.student.course.dean.name if req.student.course and req.student.course.dean else "Unknown"

        # Initialize department data if not exists
        if department_name not in department_data:
            department_data[department_name] = {
                'total': 0,
                'approved': 0,
                'denied': 0,
                'pending': 0,
                'students': set()  # Use a set to count unique students
            }

        # Update department statistics
        department_data[department_name]['total'] += 1
        department_data[department_name]['students'].add(req.student.id)

        if req.status == 'approved':
            department_data[department_name]['approved'] += 1
        elif req.status == 'denied':
            department_data[department_name]['denied'] += 1
        else:  # pending
            department_data[department_name]['pending'] += 1

    # Department summary table
    elements.append(Paragraph("Department Summary", styles['Heading3']))

    dept_table_data = [
        [
            Paragraph("Department", header_style),
            Paragraph("Total Requests", header_style),
            Paragraph("Approved", header_style),
            Paragraph("Denied", header_style),
            Paragraph("Pending", header_style),
            Paragraph("Unique Students", header_style),
            Paragraph("Approval Rate", header_style)
        ]
    ]

    # Sort departments alphabetically
    sorted_departments = sorted(department_data.items())

    # Add department data rows
    for dept_name, stats in sorted_departments:
        approval_rate = (stats['approved'] / stats['total'] * 100) if stats['total'] > 0 else 0
        dept_table_data.append([
            dept_name,
            str(stats['total']),
            str(stats['approved']),
            str(stats['denied']),
            str(stats['pending']),
            str(len(stats['students'])),
            f"{approval_rate:.1f}%"
        ])

    # Add a total row
    total_requests = sum(stats['total'] for _, stats in sorted_departments)
    total_approved = sum(stats['approved'] for _, stats in sorted_departments)
    total_denied = sum(stats['denied'] for _, stats in sorted_departments)
    total_pending = sum(stats['pending'] for _, stats in sorted_departments)

    # Get unique students across all departments
    all_students = set()
    for _, stats in sorted_departments:
        all_students.update(stats['students'])

    total_approval_rate = (total_approved / total_requests * 100) if total_requests > 0 else 0

    dept_table_data.append([
        "TOTAL",
        str(total_requests),
        str(total_approved),
        str(total_denied),
        str(total_pending),
        str(len(all_students)),
        f"{total_approval_rate:.1f}%"
    ])

    # Create and style the department summary table
    dept_table = Table(dept_table_data, repeatRows=1)
    dept_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), EMERALD_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), EMERALD_PALE),  # Total row
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, EMERALD_MEDIUM),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ])

    # Add alternating row colors
    for i in range(1, len(dept_table_data)-1):  # Skip the header and total rows
        if i % 2 == 0:
            dept_table_style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)

    dept_table.setStyle(dept_table_style)
    elements.append(dept_table)
    elements.append(Spacer(1, 0.5*inch))

    # Detailed clearance requests table
    elements.append(Paragraph("Detailed Clearance Requests", styles['Heading3']))

    data = [
        [
            Paragraph("Student ID", header_style),
            Paragraph("Name", header_style),
            Paragraph("Department", header_style),
            Paragraph("Course", header_style),
            Paragraph("Year Level", header_style),
            Paragraph("Status", header_style),
            Paragraph("Request Date", header_style)
        ]
    ]

    # Add request data
    for req in clearance_requests:
        request_date = req.request_date.strftime('%Y-%m-%d') if req.request_date else 'N/A'
        department_name = req.student.course.dean.name if req.student.course and req.student.course.dean else "Unknown"
        year_level_text = {
            1: "1st Year",
            2: "2nd Year",
            3: "3rd Year",
            4: "4th Year",
            5: "5th Year"
        }.get(req.student.year_level, f"{req.student.year_level} Year")

        data.append([
            req.student.student_id,
            f"{req.student.user.first_name} {req.student.user.last_name}",
            department_name,
            req.student.course.name if req.student.course else "N/A",
            year_level_text,
            req.status.capitalize() if req.status else 'N/A',
            request_date
        ])

    # Create the table
    table = Table(data, repeatRows=1)

    # Style the table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), EMERALD_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, EMERALD_MEDIUM),
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
            table_style.add('BACKGROUND', (0, i), (-1, i), EMERALD_PALE)

    # Color-code status column
    for i in range(1, len(data)):
        status = data[i][5].lower()
        if 'approved' in status:
            table_style.add('TEXTCOLOR', (5, i), (5, i), EMERALD_MEDIUM)
        elif 'denied' in status:
            table_style.add('TEXTCOLOR', (5, i), (5, i), RED_MEDIUM)
        elif 'pending' in status:
            table_style.add('TEXTCOLOR', (5, i), (5, i), YELLOW_MEDIUM)

    table.setStyle(table_style)
    elements.append(table)

    # Add page numbers
    elements.append(PageNumberFooter())

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf