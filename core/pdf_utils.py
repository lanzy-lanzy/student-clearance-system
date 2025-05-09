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

# Custom flowable for page numbers
class PageNumberFooter(Flowable):
    def __init__(self, page_size=letter):
        Flowable.__init__(self)
        self.page_size = page_size
        self.width = page_size[0]
        self.height = 0.5 * inch

    def draw(self):
        canvas = self.canv
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(GRAY_MEDIUM)

        # Draw the page number
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(self.width - 0.5*inch, 0.25*inch, text)

        # Draw the date
        date_text = datetime.now().strftime("%Y-%m-%d %H:%M")
        canvas.drawString(0.5*inch, 0.25*inch, f"Generated: {date_text}")

        # Draw a thin line above the footer
        canvas.setStrokeColor(EMERALD_LIGHT)
        canvas.line(0.5*inch, 0.5*inch, self.width - 0.5*inch, 0.5*inch)

        canvas.restoreState()

# Function to get the school logo path
def get_logo_path():
    # Try to find a logo in the static files
    logo_path = os.path.join(settings.STATIC_ROOT, 'img', 'logo.png')
    if os.path.exists(logo_path):
        return logo_path

    # If not found, try the media directory
    logo_path = os.path.join(settings.MEDIA_ROOT, 'logo.png')
    if os.path.exists(logo_path):
        return logo_path

    # If still not found, return None
    return None

def generate_students_pdf(students, request=None, school_year=None, semester=None, department=None):
    """
    Generate a PDF report of students
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=20,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=EMERALD_DARK
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
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

    # Enhanced normal style
    enhanced_normal = ParagraphStyle(
        'EnhancedNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=6
    )

    # Style for section headers
    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=EMERALD_DARK,
        spaceAfter=10,
        spaceBefore=15
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
    title = Paragraph("Student List Report", title_style)
    elements.append(title)

    # Subtitle with school year and semester
    if school_year and semester:
        semester_display = dict(SEMESTER_CHOICES).get(semester, semester)
        subtitle_text = f"School Year: {school_year} | Semester: {semester_display}"
        if department:
            from core.models import Dean
            try:
                dean = Dean.objects.get(id=department)
                subtitle_text += f" | Department: {dean.name}"
            except:
                pass
        subtitle = Paragraph(subtitle_text, subtitle_style)
        elements.append(subtitle)

    # Current date
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", enhanced_normal)
    date_text.alignment = TA_CENTER
    elements.append(date_text)
    elements.append(Spacer(1, 0.25*inch))

    # Create paragraph styles for table cells
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        wordWrap='CJK',
    )

    # Define column widths for better layout
    col_widths = [
        0.7*inch,    # Student ID
        1.2*inch,    # Name
        1.5*inch,    # Email
        1.8*inch,    # Course
        0.8*inch,    # Year Level
        0.9*inch,    # Contact
        0.7*inch,    # Status
        0.9*inch,    # Residence
    ]

    # Table data with paragraphs for proper text wrapping
    data = [
        [
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

    # Add student data with paragraphs for proper text wrapping
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

        # Format name as last name, first name for better sorting and display
        name = f"{student.user.last_name}, {student.user.first_name}"

        data.append([
            Paragraph(student.student_id, cell_style),
            Paragraph(name, cell_style),
            Paragraph(student.user.email, cell_style),
            Paragraph(student.course.name if student.course else "N/A", cell_style),
            Paragraph(year_level_text, cell_style),
            Paragraph(student.contact_number or "N/A", cell_style),
            Paragraph(status, cell_style),
            Paragraph(residence, cell_style)
        ])

    # Create the table with specific column widths
    table = Table(data, repeatRows=1, colWidths=col_widths)

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
    elements.append(Paragraph("Summary Statistics", section_header))

    # Group by course and year level
    course_counts = {}
    year_level_counts = {}
    status_counts = {'Approved': 0, 'Pending': 0}
    residence_counts = {'Boarder': 0, 'Non-Boarder': 0}

    for student in students:
        # Count by course
        course_name = student.course.name if student.course else "Unknown"
        if course_name not in course_counts:
            course_counts[course_name] = 0
        course_counts[course_name] += 1

        # Count by year level
        year_level = student.year_level
        if year_level not in year_level_counts:
            year_level_counts[year_level] = 0
        year_level_counts[year_level] += 1

        # Count by status
        status = "Approved" if student.is_approved else "Pending"
        status_counts[status] += 1

        # Count by residence
        residence = "Boarder" if student.is_boarder else "Non-Boarder"
        residence_counts[residence] += 1

    # Create a more structured summary table with headers
    summary_data = [
        ["Category", "Count", "Percentage"],
        ["Total Students", str(len(students)), "100%"],
        ["Approved Students", str(status_counts['Approved']), f"{(status_counts['Approved']/len(students)*100) if len(students) > 0 else 0:.1f}%"],
        ["Pending Students", str(status_counts['Pending']), f"{(status_counts['Pending']/len(students)*100) if len(students) > 0 else 0:.1f}%"],
        ["Boarders", str(residence_counts['Boarder']), f"{(residence_counts['Boarder']/len(students)*100) if len(students) > 0 else 0:.1f}%"],
        ["Non-Boarders", str(residence_counts['Non-Boarder']), f"{(residence_counts['Non-Boarder']/len(students)*100) if len(students) > 0 else 0:.1f}%"]
    ]

    # Create the summary table with better column widths
    summary_table = Table(summary_data, colWidths=[2*inch, 1*inch, 1.2*inch], repeatRows=1)

    # Style the summary table
    summary_style = TableStyle([
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), EMERALD_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),

        # Data rows styling
        ('BACKGROUND', (0, 1), (-1, 1), EMERALD_PALE),  # Total row with special background
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),  # Bold category names
        ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, EMERALD_MEDIUM),
    ])

    # Add alternating row colors
    for i in range(2, len(summary_data)):
        if i % 2 == 0:
            summary_style.add('BACKGROUND', (0, i), (-1, i), EMERALD_PALE)

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


def generate_students_by_year_level_pdf(students, request=None, school_year=None, semester=None, department=None, exam_type=None):
    """
    Generate a PDF report of students grouped by year level for departments
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=EMERALD_DARK
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
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

    year_header_style = ParagraphStyle(
        'YearHeader',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=EMERALD_DARK,
        spaceBefore=15,
        spaceAfter=10
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontSize=16,
        textColor=EMERALD_DARK,
        spaceBefore=20,
        spaceAfter=10
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
    title = Paragraph("Students by Year Level", title_style)
    elements.append(title)

    # Subtitle with school year and semester
    if school_year and semester:
        semester_display = dict(SEMESTER_CHOICES).get(semester, semester)
        exam_display = exam_type if exam_type else "Midterm"
        subtitle_text = f"School Year: {school_year} | Semester: {semester_display} - {exam_display} Records"
        if department:
            from core.models import Dean
            try:
                dean = Dean.objects.get(id=department)
                subtitle_text += f" | Department: {dean.name}"
            except:
                pass
        subtitle = Paragraph(subtitle_text, subtitle_style)
        elements.append(subtitle)

    # Current date
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", normal_style)
    elements.append(date_text)
    elements.append(Spacer(1, 0.25*inch))

    # Group students by year level
    students_by_year = {}
    for student in students:
        year_level = student.year_level
        if year_level not in students_by_year:
            students_by_year[year_level] = []
        students_by_year[year_level].append(student)

    # Sort year levels
    sorted_years = sorted(students_by_year.keys())

    # First section: Summary statistics
    elements.append(Paragraph("Summary Statistics", section_header_style))

    # Create summary table
    summary_data = [["Year Level", "Total Students", "Cleared", "Pending", "Not Started", "Clearance Rate"]]
    total_students = 0
    total_cleared = 0
    total_pending = 0
    total_not_started = 0

    for year in sorted_years:
        year_text = {
            1: "First Year",
            2: "Second Year",
            3: "Third Year",
            4: "Fourth Year",
            5: "Fifth Year"
        }.get(year, f"Year {year}")

        year_students = students_by_year[year]
        count = len(year_students)
        total_students += count

        # Count cleared, pending, and not started students
        cleared = sum(1 for s in year_students if hasattr(s, 'is_approved') and s.is_approved)
        pending = sum(1 for s in year_students if hasattr(s, 'is_approved') and not s.is_approved)
        not_started = count - (cleared + pending)

        total_cleared += cleared
        total_pending += pending
        total_not_started += not_started

        # Calculate clearance rate
        clearance_rate = f"{(cleared / count * 100) if count > 0 else 0:.1f}%"

        summary_data.append([
            year_text,
            str(count),
            str(cleared),
            str(pending),
            str(not_started),
            clearance_rate
        ])

    # Add total row
    total_clearance_rate = f"{(total_cleared / total_students * 100) if total_students > 0 else 0:.1f}%"
    summary_data.append([
        "Total",
        str(total_students),
        str(total_cleared),
        str(total_pending),
        str(total_not_started),
        total_clearance_rate
    ])

    # Create and style the summary table
    summary_table = Table(summary_data, repeatRows=1)
    summary_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), EMERALD_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, EMERALD_MEDIUM),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])

    # Style the total row
    summary_style.add('BACKGROUND', (0, -1), (-1, -1), EMERALD_PALE)
    summary_style.add('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')

    # Add alternating row colors for the summary table
    for i in range(1, len(summary_data)-1):
        if i % 2 == 0:
            summary_style.add('BACKGROUND', (0, i), (-1, i), EMERALD_PALE)

    summary_table.setStyle(summary_style)
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))

    # Add the students list table right after the summary
    elements.append(Paragraph("Students List", section_header_style))

    # Create a comprehensive student list sorted by year level and then alphabetically
    all_students = []
    for year_students in students_by_year.values():
        all_students.extend(year_students)

    # Sort students by year level first, then alphabetically by last name, then first name
    all_students.sort(key=lambda s: (s.year_level, s.user.last_name.lower(), s.user.first_name.lower()))

    # Table header for students list
    students_list_data = [
        [
            Paragraph("Student ID", header_style),
            Paragraph("Name", header_style),
            Paragraph("Year Level", header_style),
            Paragraph("Course", header_style),
            Paragraph("Status", header_style)
        ]
    ]

    # Add all students to the list
    for student in all_students:
        year_level_text = {
            1: "1st Year",
            2: "2nd Year",
            3: "3rd Year",
            4: "4th Year",
            5: "5th Year"
        }.get(student.year_level, f"{student.year_level} Year")

        status = "Cleared" if (hasattr(student, 'is_approved') and student.is_approved) else "Pending"

        students_list_data.append([
            student.student_id,
            f"{student.user.last_name}, {student.user.first_name}",
            year_level_text,
            student.course.name if student.course else "N/A",
            status
        ])

    # Create the students list table
    students_list_table = Table(students_list_data, repeatRows=1)

    # Style the students list table
    students_list_style = TableStyle([
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

    # Add alternating row colors for the students list
    for i in range(1, len(students_list_data)):
        if i % 2 == 0:
            students_list_style.add('BACKGROUND', (0, i), (-1, i), EMERALD_PALE)

    students_list_table.setStyle(students_list_style)
    elements.append(students_list_table)
    elements.append(Spacer(1, 0.3*inch))

    # Second section: Detailed student lists by year level
    elements.append(Paragraph("Detailed Student Lists by Year Level", section_header_style))

    # Process each year level
    for year in sorted_years:
        year_students = students_by_year[year]

        # Year level header
        year_text = {
            1: "First Year Students",
            2: "Second Year Students",
            3: "Third Year Students",
            4: "Fourth Year Students",
            5: "Fifth Year Students"
        }.get(year, f"Year {year} Students")

        elements.append(Paragraph(year_text, year_header_style))

        # Table header
        data = [
            [
                Paragraph("Student ID", header_style),
                Paragraph("Name", header_style),
                Paragraph("Course", header_style),
                Paragraph("Contact", header_style),
                Paragraph("Status", header_style)
            ]
        ]

        # Add student data for this year level
        for student in year_students:
            status = "Approved" if student.is_approved else "Pending"

            data.append([
                student.student_id,
                f"{student.user.first_name} {student.user.last_name}",
                student.course.name if student.course else "N/A",
                student.contact_number or "N/A",
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

        # Add year level summary
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(f"Total {year_text}: {len(year_students)}", normal_style))
        elements.append(Spacer(1, 0.3*inch))

    # Third section: Complete Student Namelist
    elements.append(Paragraph("Complete Student Namelist", section_header_style))

    # Create a comprehensive student list sorted alphabetically
    all_students = []
    for year_students in students_by_year.values():
        all_students.extend(year_students)

    # Sort students alphabetically by last name, then first name
    all_students.sort(key=lambda s: (s.user.last_name.lower(), s.user.first_name.lower()))

    # Table header for complete namelist
    namelist_data = [
        [
            Paragraph("Student ID", header_style),
            Paragraph("Last Name", header_style),
            Paragraph("First Name", header_style),
            Paragraph("Year Level", header_style),
            Paragraph("Course", header_style),
            Paragraph("Status", header_style)
        ]
    ]

    # Add all students to the namelist
    for student in all_students:
        year_level_text = {
            1: "1st Year",
            2: "2nd Year",
            3: "3rd Year",
            4: "4th Year",
            5: "5th Year"
        }.get(student.year_level, f"{student.year_level} Year")

        status = "Approved" if student.is_approved else "Pending"

        namelist_data.append([
            student.student_id,
            student.user.last_name,
            student.user.first_name,
            year_level_text,
            student.course.name if student.course else "N/A",
            status
        ])

    # Create the namelist table
    namelist_table = Table(namelist_data, repeatRows=1)

    # Style the namelist table
    namelist_style = TableStyle([
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

    # Add alternating row colors for the namelist
    for i in range(1, len(namelist_data)):
        if i % 2 == 0:
            namelist_style.add('BACKGROUND', (0, i), (-1, i), EMERALD_PALE)

    namelist_table.setStyle(namelist_style)
    elements.append(namelist_table)

    # Add total count for the namelist
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(f"Total Students: {len(all_students)}", normal_style))

    # Add page numbers
    elements.append(PageNumberFooter())

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf



def generate_clearance_summary_pdf(report_data, request=None, school_year=None, semester=None):
    """
    Generate a PDF summary report of clearance status
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
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
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
    title = Paragraph("Clearance Summary Report", title_style)
    elements.append(title)

    # Subtitle with school year and semester
    if school_year and semester:
        subtitle = Paragraph(f"School Year: {school_year} | Semester: {semester}", subtitle_style)
        elements.append(subtitle)

    # Current date
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", normal_style)
    elements.append(date_text)
    elements.append(Spacer(1, 0.5*inch))

    # Summary statistics
    elements.append(Paragraph("Clearance Statistics", styles['Heading3']))
    elements.append(Spacer(1, 0.1*inch))

    # Create a table for the summary data
    data = [
        ["Metric", "Value"],
        ["Total Students", str(report_data['total_students'])],
        ["Cleared Students", str(report_data['cleared_students'])],
        ["Pending Students", str(report_data['pending_students'])],
        ["Clearance Rate", f"{report_data['clearance_rate']}%"]
    ]

    table = Table(data, colWidths=[2.5*inch, 1.5*inch])

    # Style the table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (1, -1), 10),
        ('TOPPADDING', (0, 1), (1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (1, -1), 6),
    ])

    # Highlight the clearance rate row
    table_style.add('BACKGROUND', (0, 4), (1, 4), colors.lightgreen)
    table_style.add('FONTNAME', (0, 4), (1, 4), 'Helvetica-Bold')

    table.setStyle(table_style)
    elements.append(table)

    # Add a visual representation (bar chart)
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Visual Representation", styles['Heading3']))
    elements.append(Spacer(1, 0.1*inch))

    # Create a simple bar chart using tables
    cleared_percentage = report_data['clearance_rate']
    pending_percentage = 100 - cleared_percentage

    chart_data = [
        ["Status", "Percentage"],
        ["Cleared", f"{cleared_percentage}%"],
        ["Pending", f"{pending_percentage}%"]
    ]

    chart_table = Table(chart_data, colWidths=[1.5*inch, 4*inch])

    chart_style = TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (1, -1), 1, colors.black),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),
    ])

    # Add colored bars
    chart_style.add('BACKGROUND', (0, 1), (0, 1), colors.lightgreen)
    chart_style.add('BACKGROUND', (0, 2), (0, 2), colors.lightcoral)

    chart_table.setStyle(chart_style)
    elements.append(chart_table)

    # Add recommendations based on clearance rate
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Recommendations", styles['Heading3']))
    elements.append(Spacer(1, 0.1*inch))

    if cleared_percentage < 50:
        recommendation = "The clearance rate is below 50%. Consider implementing additional support measures to help students complete their clearance requirements."
    elif cleared_percentage < 75:
        recommendation = "The clearance rate is moderate. Continue monitoring progress and provide targeted assistance to students with pending clearances."
    else:
        recommendation = "The clearance rate is excellent. Maintain current processes and consider recognizing offices with high clearance efficiency."

    elements.append(Paragraph(recommendation, normal_style))

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf

def generate_pending_clearances_pdf(clearance_requests, request=None, school_year=None, semester=None, department=None):
    """
    Generate a PDF report of pending clearance requests
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=20,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=EMERALD_DARK
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
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

    # Enhanced normal style
    enhanced_normal = ParagraphStyle(
        'EnhancedNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=6
    )

    # Style for section headers
    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=EMERALD_DARK,
        spaceAfter=10,
        spaceBefore=15
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
    title = Paragraph("Pending Clearance Requests Report", title_style)
    elements.append(title)

    # Subtitle with school year and semester
    semester_display = dict(SEMESTER_CHOICES).get(semester, semester)
    if school_year and semester:
        subtitle_text = f"School Year: {school_year} | Semester: {semester_display}"
        if department:
            from core.models import Dean
            try:
                dean = Dean.objects.get(id=department)
                subtitle_text += f" | Department: {dean.name}"
            except:
                pass
        subtitle = Paragraph(subtitle_text, subtitle_style)
        elements.append(subtitle)

    # Current date
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", enhanced_normal)
    date_text.alignment = TA_CENTER
    elements.append(date_text)
    elements.append(Spacer(1, 0.25*inch))

    # Summary section
    elements.append(Paragraph("Summary", section_header))

    # Group by office
    office_counts = {}
    student_counts = {}

    for req in clearance_requests:
        office_name = req.office.name
        if office_name not in office_counts:
            office_counts[office_name] = 0
        office_counts[office_name] += 1

        student_id = req.student.id
        if student_id not in student_counts:
            student_counts[student_id] = 0
        student_counts[student_id] += 1

    # Summary data
    summary_data = [
        ["Total Pending Requests:", str(len(clearance_requests))],
        ["Unique Students:", str(len(student_counts))],
        ["Unique Offices:", str(len(office_counts))],
        ["Average Requests per Student:", f"{len(clearance_requests) / len(student_counts):.1f}" if student_counts else "0"],
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), EMERALD_PALE),
        ('TEXTCOLOR', (0, 0), (0, -1), EMERALD_DARK),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, EMERALD_MEDIUM),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 0.25*inch))

    # Office distribution
    if office_counts:
        elements.append(Paragraph("Pending Requests by Office", section_header))

        office_data = [
            [
                Paragraph("Office", header_style),
                Paragraph("Pending Requests", header_style),
                Paragraph("Percentage", header_style)
            ]
        ]

        # Sort offices by count (descending)
        sorted_offices = sorted(office_counts.items(), key=lambda x: x[1], reverse=True)

        for office_name, count in sorted_offices:
            percentage = (count / len(clearance_requests)) * 100
            office_data.append([
                office_name,
                str(count),
                f"{percentage:.1f}%"
            ])

        # Add a total row
        office_data.append([
            "TOTAL",
            str(len(clearance_requests)),
            "100.0%"
        ])

        office_table = Table(office_data, colWidths=[4*inch, 2*inch, 2*inch], repeatRows=1)

        office_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BLUE_MEDIUM),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('BACKGROUND', (0, -1), (-1, -1), EMERALD_PALE),  # Total row
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ])

        # Add alternating row colors
        for i in range(1, len(office_data)-1):  # Skip the header and total rows
            if i % 2 == 0:
                office_style.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)

        office_table.setStyle(office_style)
        elements.append(office_table)
        elements.append(Spacer(1, 0.25*inch))

    # Detailed requests table
    elements.append(Paragraph("Detailed Pending Clearance Requests", section_header))

    # Table data
    data = [
        [
            Paragraph("Student ID", header_style),
            Paragraph("Student Name", header_style),
            Paragraph("Course", header_style),
            Paragraph("Office", header_style),
            Paragraph("Submission Date", header_style)
        ]
    ]

    # Add request data
    for req in clearance_requests:
        student = req.student
        submission_date = req.created_at.strftime("%Y-%m-%d") if req.created_at else "N/A"

        data.append([
            student.student_id,
            f"{student.user.first_name} {student.user.last_name}",
            student.course.name if student.course else "N/A",
            req.office.name,
            submission_date
        ])

    # Create the table
    table = Table(data, repeatRows=1)

    # Style the table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), BLUE_MEDIUM),
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

    # Add page numbers
    elements.append(PageNumberFooter())

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf

def generate_cleared_students_pdf(clearances, request=None, school_year=None, semester=None, department=None):
    """
    Generate a PDF report of students with cleared clearance status
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
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12,
        textColor=EMERALD_DARK
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
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

    # Enhanced normal style
    enhanced_normal = ParagraphStyle(
        'EnhancedNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=6
    )

    # Style for section headers
    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=EMERALD_DARK,
        spaceAfter=10,
        spaceBefore=15
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
    title = Paragraph("Cleared Students Report", title_style)
    elements.append(title)

    # Subtitle with school year and semester
    if school_year and semester:
        semester_display = dict(SEMESTER_CHOICES).get(semester, semester)
        subtitle_text = f"School Year: {school_year} | Semester: {semester_display}"
        if department:
            from core.models import Dean
            try:
                dean = Dean.objects.get(id=department)
                subtitle_text += f" | Department: {dean.name}"
            except:
                pass
        subtitle = Paragraph(subtitle_text, subtitle_style)
        elements.append(subtitle)

    # Current date
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", enhanced_normal)
    date_text.alignment = TA_CENTER
    elements.append(date_text)
    elements.append(Spacer(1, 0.25*inch))

    # Summary section
    elements.append(Paragraph("Summary", section_header))

    # Group by course and year level
    course_counts = {}
    year_level_counts = {}

    for clearance in clearances:
        student = clearance.student

        # Count by course
        course_name = student.course.name if student.course else "No Course"
        if course_name not in course_counts:
            course_counts[course_name] = 0
        course_counts[course_name] += 1

        # Count by year level
        year_level = student.year_level
        if year_level not in year_level_counts:
            year_level_counts[year_level] = 0
        year_level_counts[year_level] += 1

    # Summary data
    summary_data = [
        ["Total Cleared Students:", str(len(clearances))],
        ["Unique Courses:", str(len(course_counts))],
        ["Earliest Clearance Date:", min([c.cleared_date for c in clearances if c.cleared_date]).strftime("%Y-%m-%d") if any(c.cleared_date for c in clearances) else "N/A"],
        ["Latest Clearance Date:", max([c.cleared_date for c in clearances if c.cleared_date]).strftime("%Y-%m-%d") if any(c.cleared_date for c in clearances) else "N/A"],
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), EMERALD_PALE),
        ('TEXTCOLOR', (0, 0), (0, -1), EMERALD_DARK),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, EMERALD_MEDIUM),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 0.25*inch))

    # Distribution by Year Level
    if year_level_counts:
        elements.append(Paragraph("Cleared Students by Year Level", section_header))

        year_level_data = [
            [
                Paragraph("Year Level", header_style),
                Paragraph("Number of Students", header_style),
                Paragraph("Percentage", header_style)
            ]
        ]

        # Sort year levels
        sorted_year_levels = sorted(year_level_counts.items())

        for year_level, count in sorted_year_levels:
            year_level_text = {
                1: "1st Year",
                2: "2nd Year",
                3: "3rd Year",
                4: "4th Year",
                5: "5th Year"
            }.get(year_level, f"{year_level} Year")

            percentage = (count / len(clearances)) * 100
            year_level_data.append([
                year_level_text,
                str(count),
                f"{percentage:.1f}%"
            ])

        # Add a total row
        year_level_data.append([
            "TOTAL",
            str(len(clearances)),
            "100.0%"
        ])

        year_level_table = Table(year_level_data, colWidths=[2*inch, 2*inch, 2*inch], repeatRows=1)

        year_level_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), EMERALD_DARK),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('BACKGROUND', (0, -1), (-1, -1), EMERALD_PALE),  # Total row
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
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

    # Create paragraph styles for table cells
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        wordWrap='CJK',
    )

    # Define column widths for better layout
    col_widths = [
        0.8*inch,    # Student ID
        1.5*inch,    # Name
        2.0*inch,    # Course
        0.9*inch,    # Year Level
        1.0*inch,    # Contact
        1.0*inch,    # Date Cleared
    ]

    # Table data with paragraphs for proper text wrapping
    data = [
        [
            Paragraph("Student ID", header_style),
            Paragraph("Student Name", header_style),
            Paragraph("Course", header_style),
            Paragraph("Year Level", header_style),
            Paragraph("Contact Number", header_style),
            Paragraph("Date Cleared", header_style)
        ]
    ]

    # Sort clearances by student last name for better organization
    sorted_clearances = sorted(clearances, key=lambda c: f"{c.student.user.last_name}, {c.student.user.first_name}".lower())

    # Add student data with paragraphs for proper text wrapping
    for clearance in sorted_clearances:
        student = clearance.student
        year_level_text = {
            1: "1st Year",
            2: "2nd Year",
            3: "3rd Year",
            4: "4th Year",
            5: "5th Year"
        }.get(student.year_level, f"{student.year_level} Year")

        cleared_date = clearance.cleared_date.strftime("%Y-%m-%d") if clearance.cleared_date else "N/A"

        # Format name as last name, first name for better sorting and display
        name = f"{student.user.last_name}, {student.user.first_name}"

        data.append([
            Paragraph(student.student_id, cell_style),
            Paragraph(name, cell_style),
            Paragraph(student.course.name if student.course else "N/A", cell_style),
            Paragraph(year_level_text, cell_style),
            Paragraph(student.contact_number or "N/A", cell_style),
            Paragraph(cleared_date, cell_style)
        ])

    # Create the table with specific column widths
    table = Table(data, repeatRows=1, colWidths=col_widths)

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

def generate_course_statistics_pdf(course_stats, request=None, school_year=None, semester=None, department=None):
    """
    Generate a PDF report of clearance statistics by course
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
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        fontSize=14,
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
    title = Paragraph("Course Statistics Report", title_style)
    elements.append(title)

    # Subtitle with school year and semester
    if school_year and semester:
        subtitle_text = f"School Year: {school_year} | Semester: {semester}"
        if department:
            from core.models import Dean
            try:
                dean = Dean.objects.get(id=department)
                subtitle_text += f" | Department: {dean.name}"
            except:
                pass
        subtitle = Paragraph(subtitle_text, subtitle_style)
        elements.append(subtitle)

    # Current date
    date_text = Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", normal_style)
    elements.append(date_text)
    elements.append(Spacer(1, 0.25*inch))

    # Table data
    data = [
        [
            Paragraph("Course", header_style),
            Paragraph("Total Students", header_style),
            Paragraph("Cleared", header_style),
            Paragraph("Pending", header_style),
            Paragraph("Clearance Rate", header_style)
        ]
    ]

    # Add course data
    for stat in course_stats:
        data.append([
            stat['course'],
            str(stat['total']),
            str(stat['cleared']),
            str(stat['pending']),
            f"{stat['clearance_rate']}%"
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
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
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

    # Highlight high and low clearance rates
    for i in range(1, len(data)):
        rate = float(data[i][4].replace('%', ''))
        if rate >= 90:
            table_style.add('BACKGROUND', (4, i), (4, i), EMERALD_LIGHT)
        elif rate <= 50:
            table_style.add('BACKGROUND', (4, i), (4, i), RED_MEDIUM)

    table.setStyle(table_style)
    elements.append(table)

    # Summary section
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Summary Analysis", styles['Heading3']))
    elements.append(Spacer(1, 0.1*inch))

    # Calculate overall statistics
    total_students = sum(stat['total'] for stat in course_stats)
    total_cleared = sum(stat['cleared'] for stat in course_stats)
    total_pending = sum(stat['pending'] for stat in course_stats)
    overall_rate = round((total_cleared / total_students * 100) if total_students > 0 else 0, 2)

    # Find courses with highest and lowest clearance rates
    if course_stats:
        sorted_by_rate = sorted(course_stats, key=lambda x: x['clearance_rate'])
        lowest_course = sorted_by_rate[0]
        highest_course = sorted_by_rate[-1]

        summary_text = f"""Overall Statistics:
        - Total Students Across All Courses: {total_students}
        - Total Cleared: {total_cleared} ({overall_rate}%)
        - Total Pending: {total_pending}

        Course with Highest Clearance Rate: {highest_course['course']} ({highest_course['clearance_rate']}%)
        Course with Lowest Clearance Rate: {lowest_course['course']} ({lowest_course['clearance_rate']}%)
        """
    else:
        summary_text = "No course data available for analysis."

    elements.append(Paragraph(summary_text, normal_style))

    # Add page numbers
    elements.append(PageNumberFooter())

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf
