from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
import random
from core.models import (
    Dean, Course, Office, Staff, Student,
    ProgramChair, Clearance, ClearanceRequest
)


class Command(BaseCommand):
    help = 'Base command for populating the database with customizable data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            action='store_true',
            help='Create basic users (admin, staff, program chairs)',
        )
        parser.add_argument(
            '--students',
            action='store_true',
            help='Create sample students',
        )
        parser.add_argument(
            '--clearances',
            action='store_true',
            help='Create clearance records for students',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of sample records to create',
        )
        parser.add_argument(
            '--school-year',
            type=str,
            help='School year in format YYYY-YYYY',
        )
        parser.add_argument(
            '--semester',
            type=str,
            choices=['1ST', '2ND', 'SUM'],
            help='Semester (1ST, 2ND, or SUM)',
        )

    def handle(self, *args, **options):
        # Set default school year and semester if not provided
        if not options.get('school_year'):
            current_year = timezone.now().year
            options['school_year'] = f"{current_year}-{current_year + 1}"

        if not options.get('semester'):
            options['semester'] = "1ST"

        self.stdout.write(self.style.SUCCESS(f"Using school year: {options['school_year']} and semester: {options['semester']}"))

        # Create basic structure if needed
        self.create_basic_structure()

        # Create users if requested
        if options['users']:
            self.create_users(options['count'])

        # Create students if requested
        if options['students']:
            self.create_students(options['count'], options['school_year'], options['semester'])

        # Create clearances if requested
        if options['clearances']:
            self.create_clearances(options['school_year'], options['semester'])

        # If no specific options were selected, run everything
        if not (options['users'] or options['students'] or options['clearances']):
            self.stdout.write(self.style.WARNING("No specific options selected. Running all operations."))
            self.create_users(options['count'])
            self.create_students(options['count'], options['school_year'], options['semester'])
            self.create_clearances(options['school_year'], options['semester'])

        self.stdout.write(self.style.SUCCESS("Data population completed successfully!"))

    def create_basic_structure(self):
        """Create the basic structure needed for the system (deans, courses, offices)"""
        self.stdout.write(self.style.SUCCESS("\nCreating basic structure..."))

        # Create admin user if it doesn't exist
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "is_staff": True,
                "is_superuser": True,
                "first_name": "Admin",
                "last_name": "User"
            }
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user"))
        else:
            self.stdout.write(self.style.WARNING("Admin user already exists"))

        # Create Deans
        deans_data = [
            {
                "name": "SET DEAN",
                "description": "School of Engineering and Technology"
            },
            {
                "name": "STE DEAN",
                "description": "School of Teacher Education"
            },
            {
                "name": "SOCJE DEAN",
                "description": "School of Criminal Justice Education"
            },
            {
                "name": "SAFES DEAN",
                "description": "School of Agriculture, Forestry and Environmental Sciences"
            }
        ]

        for dean_data in deans_data:
            dean, created = Dean.objects.get_or_create(
                name=dean_data["name"],
                defaults={"description": dean_data["description"]}
            )
            self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Found'} dean: {dean.name}"))

        # Create Courses
        courses_data = [
            {"code": "BSIT", "name": "Bachelor of Science in Information Technology", "dean_name": "SET DEAN"},
            {"code": "BSCS", "name": "Bachelor of Science in Computer Science", "dean_name": "SET DEAN"},
            {"code": "BEED", "name": "Bachelor of Elementary Education", "dean_name": "STE DEAN"},
            {"code": "BSED", "name": "Bachelor of Secondary Education", "dean_name": "STE DEAN"},
            {"code": "BSCrim", "name": "Bachelor of Science in Criminology", "dean_name": "SOCJE DEAN"},
            {"code": "BSAF", "name": "Bachelor of Science in Agroforestry", "dean_name": "SAFES DEAN"},
            {"code": "BSA", "name": "Bachelor of Science in Agriculture", "dean_name": "SAFES DEAN"}
        ]

        for course_data in courses_data:
            dean = Dean.objects.get(name=course_data["dean_name"])
            course, created = Course.objects.get_or_create(
                code=course_data["code"],
                defaults={
                    "name": course_data["name"],
                    "dean": dean
                }
            )
            self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Found'} course: {course.code}"))

        # Create Offices
        self.create_offices()

    def create_offices(self):
        """Create the necessary offices for the system"""
        created_count = 0
        offices = [
            # Base offices that all students must pass
            {
                "name": "OSA",
                "description": "Office of Student Affairs",
                "office_type": "OTHER"
            },
            {
                "name": "DSA",
                "description": "Dean of Student Affairs",
                "office_type": "OTHER"
            },
            {
                "name": "SSC",
                "description": "Student Services Center",
                "office_type": "OTHER"
            },
            {
                "name": "LIBRARY",
                "description": "University Library",
                "office_type": "OTHER"
            },
            {
                "name": "LABORATORY",
                "description": "Laboratory Services",
                "office_type": "OTHER"
            },
            {
                "name": "ACCOUNTING OFFICE",
                "description": "University Accounting Office",
                "office_type": "OTHER"
            },
            {
                "name": "REGISTRAR OFFICE",
                "description": "University Registrar",
                "office_type": "OTHER"
            },
            {
                "name": "Guidance Office",
                "description": "University Guidance Office",
                "office_type": "OTHER"
            },
            {
                "name": "DORMITORY",
                "description": "University Dormitory",
                "office_type": "OTHER"
            },
            # School-specific SSB offices
            {
                "name": "SSB SET",
                "description": "Student Services Bureau - School of Engineering and Technology",
                "office_type": "SET"
            },
            {
                "name": "SSB STE",
                "description": "Student Services Bureau - School of Teacher Education",
                "office_type": "STE"
            },
            {
                "name": "SSB SOCJE",
                "description": "Student Services Bureau - School of Criminal Justice Education",
                "office_type": "SOCJE"
            },
            {
                "name": "SSB SAFES",
                "description": "Student Services Bureau - School of Agriculture, Forestry and Environmental Sciences",
                "office_type": "SAFES"
            }
        ]

        # Get all deans for office affiliation
        deans = {dean.name: dean for dean in Dean.objects.all()}

        for office_data in offices:
            # Determine the affiliated dean based on office type
            affiliated_dean = None
            if office_data["office_type"] in ["SET", "STE", "SOCJE", "SAFES"]:
                dean_name = f"{office_data['office_type']} DEAN"
                affiliated_dean = deans.get(dean_name)

            office, created = Office.objects.get_or_create(
                name=office_data["name"],
                defaults={
                    "description": office_data["description"],
                    "office_type": office_data["office_type"],
                    "affiliated_dean": affiliated_dean
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created office: {office.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Office exists: {office.name}"))

        self.stdout.write(self.style.SUCCESS(f"\nCreated {created_count} new offices"))

    def create_users(self, count):
        """Create staff and program chair users"""
        self.stdout.write(self.style.SUCCESS("\nCreating staff members..."))

        # Create basic staff members
        staff_data = [
            {
                "username": "osa_staff",
                "password": "staff123",
                "first_name": "OSA",
                "last_name": "Staff",
                "email": "osa.staff@example.com",
                "office": "OSA",
                "role": "OSA Officer"
            },
            {
                "username": "library_staff",
                "password": "staff123",
                "first_name": "Library",
                "last_name": "Staff",
                "email": "library.staff@example.com",
                "office": "LIBRARY",
                "role": "Librarian"
            },
            {
                "username": "accounting_staff",
                "password": "staff123",
                "first_name": "Accounting",
                "last_name": "Staff",
                "email": "accounting.staff@example.com",
                "office": "ACCOUNTING OFFICE",
                "role": "Accounting Officer"
            }
        ]

        for staff_info in staff_data:
            # Create User
            user, created = User.objects.get_or_create(
                username=staff_info["username"],
                defaults={
                    "first_name": staff_info["first_name"],
                    "last_name": staff_info["last_name"],
                    "email": staff_info["email"],
                    "is_active": True
                }
            )
            if created:
                user.set_password(staff_info["password"])
                user.save()

            # Get office
            office = Office.objects.get(name=staff_info["office"])

            # Create Staff
            staff, created = Staff.objects.get_or_create(
                user=user,
                defaults={
                    "office": office,
                    "role": staff_info["role"],
                    "is_dormitory_owner": False
                }
            )

            self.stdout.write(self.style.SUCCESS(
                f"{'Created' if created else 'Found'} staff member: {staff.user.get_full_name()} ({staff.office.name})"
            ))

        # Create dormitory owners
        self.stdout.write(self.style.SUCCESS("\nCreating dormitory owners..."))
        dormitory_office = Office.objects.get(name="DORMITORY")

        for i in range(1, count + 1):
            username = f"dorm_owner{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": f"Dormitory",
                    "last_name": f"Owner {i}",
                    "email": f"dorm.owner{i}@example.com",
                    "is_active": True
                }
            )
            if created:
                user.set_password("dorm123")
                user.save()

            staff, created = Staff.objects.get_or_create(
                user=user,
                defaults={
                    "office": dormitory_office,
                    "role": f"Dormitory Owner {i}",
                    "is_dormitory_owner": True
                }
            )

            self.stdout.write(self.style.SUCCESS(
                f"{'Created' if created else 'Found'} dormitory owner: {staff.user.get_full_name()}"
            ))

        # Create program chairs
        self.stdout.write(self.style.SUCCESS("\nCreating program chairs..."))
        deans = Dean.objects.all()

        for dean in deans:
            username = f"pc_{dean.name.lower().replace(' ', '_')}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": f"Program Chair",
                    "last_name": dean.name,
                    "email": f"{username}@example.com",
                    "is_active": True
                }
            )
            if created:
                user.set_password("pc123")
                user.save()

            pc, created = ProgramChair.objects.get_or_create(
                user=user,
                defaults={
                    "dean": dean,
                    "designation": dean.name
                }
            )

            self.stdout.write(self.style.SUCCESS(
                f"{'Created' if created else 'Found'} program chair: {pc.user.get_full_name()} for {dean.name}"
            ))

    def create_students(self, count, school_year, semester):
        """Create sample students"""
        self.stdout.write(self.style.SUCCESS(f"\nCreating {count} students..."))

        courses = Course.objects.all()
        dormitory_owners = Staff.objects.filter(is_dormitory_owner=True)

        for i in range(1, count + 1):
            # Select a random course
            course = random.choice(courses)

            # Get the program chair for this course's dean
            program_chair = ProgramChair.objects.filter(dean=course.dean).first()

            # Determine if student is a boarder (50% chance)
            is_boarder = random.choice([True, False])

            # If boarder, assign a dormitory owner
            dormitory_owner = random.choice(dormitory_owners) if is_boarder and dormitory_owners.exists() else None

            # Create the user
            username = f"student_{course.code.lower()}_{i}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": f"Student{i}",
                    "last_name": f"{course.code}",
                    "email": f"{username}@student.edu",
                    "is_active": True
                }
            )

            if created:
                user.set_password("student123")
                user.save()

            # Create the student
            student_id = f"{school_year.split('-')[0][-2:]}-{course.code}-{i:03d}"
            student, created = Student.objects.get_or_create(
                user=user,
                defaults={
                    "student_id": student_id,
                    "course": course,
                    "program_chair": program_chair,
                    "dormitory_owner": dormitory_owner,
                    "year_level": random.randint(1, 4),
                    "contact_number": f"9510440{i:03d}",
                    "is_boarder": is_boarder,
                    "is_approved": True
                }
            )

            self.stdout.write(self.style.SUCCESS(
                f"{'Created' if created else 'Found'} student: {student.user.get_full_name()} ({student.student_id})"
            ))

            # Create clearance for this student
            if created:
                self.create_student_clearance(student, school_year, semester)

    def create_student_clearance(self, student, school_year, semester):
        """Create a clearance record for a student"""
        try:
            # Create the main clearance record
            clearance, created = Clearance.objects.get_or_create(
                student=student,
                school_year=school_year,
                semester=semester,
                defaults={
                    "is_cleared": False,
                    "program_chair_approved": False
                }
            )

            if not created:
                self.stdout.write(self.style.WARNING(
                    f"Clearance already exists for {student.user.get_full_name()} - {school_year} {semester}"
                ))
                return

            # Get required offices based on student's school
            required_offices = Office.objects.filter(
                Q(office_type='OTHER') |
                Q(office_type=student.course.dean.name.split()[0])  # First word of dean name (e.g., "SET" from "SET DEAN")
            )

            # Create clearance requests for each office
            for office in required_offices:
                ClearanceRequest.objects.create(
                    student=student,
                    office=office,
                    clearance=clearance,
                    school_year=school_year,
                    semester=semester,
                    status='pending',
                    request_date=timezone.now()
                )

            self.stdout.write(self.style.SUCCESS(
                f"Created clearance requests for {student.user.get_full_name()} - {school_year} {semester}"
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"Error creating clearance for {student.user.get_full_name()}: {str(e)}"
            ))

    def create_clearances(self, school_year, semester):
        """Create or update clearance records for all students"""
        self.stdout.write(self.style.SUCCESS("\nCreating/updating clearances for all students..."))

        students = Student.objects.filter(is_approved=True)

        for student in students:
            # Check if student already has a clearance for this period
            clearance = Clearance.objects.filter(
                student=student,
                school_year=school_year,
                semester=semester
            ).first()

            if clearance:
                self.stdout.write(self.style.WARNING(
                    f"Clearance already exists for {student.user.get_full_name()} - {school_year} {semester}"
                ))
                continue

            # Create new clearance
            self.create_student_clearance(student, school_year, semester)

        # Randomly approve some clearance requests (for demonstration)
        self.approve_random_clearances(school_year, semester)

    def approve_random_clearances(self, school_year, semester):
        """Randomly approve some clearance requests"""
        self.stdout.write(self.style.SUCCESS("\nRandomly approving some clearance requests..."))

        # Get all pending clearance requests
        pending_requests = ClearanceRequest.objects.filter(
            school_year=school_year,
            semester=semester,
            status='pending'
        )

        # Get staff members to use as reviewers
        staff_members = Staff.objects.all()

        if not staff_members.exists():
            self.stdout.write(self.style.ERROR("No staff members available to approve requests"))
            return

        # Approve about 70% of pending requests
        for request in pending_requests:
            if random.random() < 0.7:  # 70% chance
                # Find a staff member from the appropriate office
                reviewer = staff_members.filter(office=request.office).first()

                if reviewer:
                    request.status = 'approved'
                    request.reviewed_by = reviewer
                    request.reviewed_date = timezone.now()
                    request.save()

                    self.stdout.write(self.style.SUCCESS(
                        f"Approved clearance request for {request.student.user.get_full_name()} - {request.office.name}"
                    ))

        # Update clearance status for all students
        clearances = Clearance.objects.filter(
            school_year=school_year,
            semester=semester
        )

        for clearance in clearances:
            # Check if all requests are approved
            pending_or_denied = clearance.requests.filter(status__in=['pending', 'denied']).exists()
            clearance.is_cleared = not pending_or_denied

            if clearance.is_cleared:
                clearance.cleared_date = timezone.now()
                clearance.program_chair_approved = random.choice([True, False])  # 50% chance of program chair approval

                self.stdout.write(self.style.SUCCESS(
                    f"Clearance completed for {clearance.student.user.get_full_name()}"
                ))

            clearance.save()
