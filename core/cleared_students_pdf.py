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

def generate_cleared_students_report_pdf(clearance_requests, request=None, school_year=None, semester=None, office=None):
    """
    Generate a PDF report of students who have been cleared by a specific office
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

    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=EMERALD_DARK,
        spaceAfter=6
    )

    normal_style = styles["Normal"]
    enhanced_normal = ParagraphStyle(
        'EnhancedNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )

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
    title = Paragraph(f"{office_name} Cleared Students Report", title_style)
    elements.append(title)

    # Subtitle with school year and semester
    if school_year and semester:
        semester_display = dict(SEMESTER_CHOICES).get(semester, semester)
        subtitle = Paragraph(f"School Year: {school_year} | Semester: {semester_display}", subtitle_style)
        elements.append(subtitle)

    # Current date
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", enhanced_normal)
    date_text.alignment = TA_CENTER
    elements.append(date_text)
    elements.append(Spacer(1, 0.25*inch))

    # Summary section
    elements.append(Paragraph("Summary", section_header))

    # Count total cleared students
    total_cleared = clearance_requests.count()
    
    # Group by course
    course_counts = {}
    for req in clearance_requests:
        course_name = req.student.course.name if req.student.course else "Unknown"
        if course_name not in course_counts:
            course_counts[course_name] = 0
        course_counts[course_name] += 1
    
    # Group by year level
    year_level_counts = {}
    for req in clearance_requests:
        year_level = req.student.year_level
        if year_level not in year_level_counts:
            year_level_counts[year_level] = 0
        year_level_counts[year_level] += 1

    # Summary data
    summary_data = [
        ["Total Cleared Students:", str(total_cleared)],
        ["Unique Courses:", str(len(course_counts))],
        ["Earliest Clearance Date:", min([req.reviewed_date for req in clearance_requests if req.reviewed_date]).strftime("%Y-%m-%d") if any(req.reviewed_date for req in clearance_requests) else "N/A"],
        ["Latest Clearance Date:", max([req.reviewed_date for req in clearance_requests if req.reviewed_date]).strftime("%Y-%m-%d") if any(req.reviewed_date for req in clearance_requests) else "N/A"],
    ]

    # Create summary table
    summary_table = Table(summary_data)
    summary_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, EMERALD_LIGHT),
        ('BACKGROUND', (0, 0), (0, -1), EMERALD_PALE),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ])
    summary_table.setStyle(summary_style)
    elements.append(summary_table)
    elements.append(Spacer(1, 0.25*inch))

    # Course breakdown
    if course_counts:
        elements.append(Paragraph("Cleared Students by Course", section_header))
        
        # Sort courses by count (descending)
        sorted_courses = sorted(course_counts.items(), key=lambda x: x[1], reverse=True)
        
        course_data = [["Course", "Number of Students", "Percentage"]]
        for course, count in sorted_courses:
            percentage = f"{(count / total_cleared) * 100:.1f}%"
            course_data.append([course, str(count), percentage])
        
        # Add total row
        course_data.append(["Total", str(total_cleared), "100.0%"])
        
        course_table = Table(course_data)
        course_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), EMERALD_DARK),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), EMERALD_PALE),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, EMERALD_MEDIUM),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ])
        
        # Add alternating row colors
        for i in range(1, len(course_data)-1):  # Skip the header and total rows
            if i % 2 == 0:
                course_style.add('BACKGROUND', (0, i), (-1, i), EMERALD_PALE)
        
        course_table.setStyle(course_style)
        elements.append(course_table)
        elements.append(Spacer(1, 0.25*inch))
    
    # Year level breakdown
    if year_level_counts:
        elements.append(Paragraph("Cleared Students by Year Level", section_header))
        
        # Sort year levels
        sorted_years = sorted(year_level_counts.items())
        
        year_level_data = [["Year Level", "Number of Students", "Percentage"]]
        for year, count in sorted_years:
            year_text = {
                1: "1st Year",
                2: "2nd Year",
                3: "3rd Year",
                4: "4th Year",
                5: "5th Year"
            }.get(year, f"{year} Year")
            
            percentage = f"{(count / total_cleared) * 100:.1f}%"
            year_level_data.append([year_text, str(count), percentage])
        
        # Add total row
        year_level_data.append(["Total", str(total_cleared), "100.0%"])
        
        year_level_table = Table(year_level_data)
        year_level_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), EMERALD_DARK),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), EMERALD_PALE),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, EMERALD_MEDIUM),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ])
        
        # Add alternating row colors
        for i in range(1, len(year_level_data)-1):  # Skip the header and total rows
            if i % 2 == 0:
                year_level_style.add('BACKGROUND', (0, i), (-1, i), EMERALD_PALE)
        
        year_level_table.setStyle(year_level_style)
        elements.append(year_level_table)
        elements.append(Spacer(1, 0.25*inch))
    
    # Detailed students table
    elements.append(Paragraph("Detailed List of Cleared Students", section_header))
    
    # Table data
    data = [
        [
            Paragraph("Student ID", header_style),
            Paragraph("Student Name", header_style),
            Paragraph("Course", header_style),
            Paragraph("Year Level", header_style),
            Paragraph("Date Cleared", header_style),
            Paragraph("Cleared By", header_style)
        ]
    ]
    
    # Add student data
    for req in clearance_requests:
        student = req.student
        year_level_text = {
            1: "1st Year",
            2: "2nd Year",
            3: "3rd Year",
            4: "4th Year",
            5: "5th Year"
        }.get(student.year_level, f"{student.year_level} Year")
        
        cleared_date = req.reviewed_date.strftime("%Y-%m-%d") if req.reviewed_date else "N/A"
        
        data.append([
            student.student_id,
            f"{student.user.first_name} {student.user.last_name}",
            student.course.name if student.course else "N/A",
            year_level_text,
            cleared_date,
            req.reviewed_by.get_full_name() if req.reviewed_by else "N/A"
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
    
    # Add page numbers
    elements.append(PageNumberFooter())
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf
