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
    help = 'Populate data specifically for SAFES dean to print permits'

    def handle(self, *args, **options):
        # Get current school year and semester
        current_year = timezone.now().year
        school_year = f"{current_year}-{current_year + 1}"
        semester = "1ST"  # First semester
        
        self.stdout.write(self.style.SUCCESS(f"Using school year: {school_year} and semester: {semester}"))
        
        # Get SAFES dean
        try:
            safes_dean = Dean.objects.get(name="SAFES DEAN")
            self.stdout.write(self.style.SUCCESS(f"Found SAFES dean: {safes_dean.name}"))
        except Dean.DoesNotExist:
            self.stdout.write(self.style.ERROR("SAFES dean not found. Creating it..."))
            safes_dean = Dean.objects.create(
                name="SAFES DEAN",
                description="School of Agriculture, Forestry and Environmental Sciences"
            )
        
        # Get or create SAFES program chair
        try:
            program_chair_user = User.objects.get(username="pc_safes_dean")
            program_chair = ProgramChair.objects.get(user=program_chair_user)
            self.stdout.write(self.style.SUCCESS(f"Found program chair: {program_chair.user.get_full_name()}"))
        except (User.DoesNotExist, ProgramChair.DoesNotExist):
            self.stdout.write(self.style.ERROR("Program chair not found. Creating it..."))
            program_chair_user = User.objects.create_user(
                username="pc_safes_dean",
                password="pc123",
                first_name="SAFES",
                last_name="Program Chair",
                email="pc_safes@example.com",
                is_active=True
            )
            program_chair = ProgramChair.objects.create(
                user=program_chair_user,
                dean=safes_dean
            )
        
        # Get SAFES courses
        safes_courses = Course.objects.filter(dean=safes_dean)
        if not safes_courses.exists():
            self.stdout.write(self.style.ERROR("No SAFES courses found. Creating them..."))
            safes_courses = [
                Course.objects.create(code="BSAF", name="Bachelor of Science in Agroforestry", dean=safes_dean),
                Course.objects.create(code="BSA", name="Bachelor of Science in Agriculture", dean=safes_dean)
            ]
        else:
            self.stdout.write(self.style.SUCCESS(f"Found {safes_courses.count()} SAFES courses"))
        
        # Create students with completed clearances
        self.create_students_with_clearances(safes_courses, program_chair, school_year, semester)
        
        self.stdout.write(self.style.SUCCESS("Data population completed successfully!"))
    
    def create_students_with_clearances(self, courses, program_chair, school_year, semester):
        """Create students with completed clearances for permit printing"""
        self.stdout.write(self.style.SUCCESS("\nCreating students with completed clearances..."))
        
        # Student data
        students_data = [
            {
                "username": "safes_student1",
                "password": "student123",
                "first_name": "Maria",
                "last_name": "Santos",
                "email": "maria.santos@student.edu",
                "student_id": f"{school_year.split('-')[0][-2:]}-BSAF-001",
                "course": courses.filter(code="BSAF").first() or courses[0],
                "year_level": 3,
                "contact_number": "9510440202"
            },
            {
                "username": "safes_student2",
                "password": "student123",
                "first_name": "Juan",
                "last_name": "Cruz",
                "email": "juan.cruz@student.edu",
                "student_id": f"{school_year.split('-')[0][-2:]}-BSA-002",
                "course": courses.filter(code="BSA").first() or courses[0],
                "year_level": 4,
                "contact_number": "9510440202"
            },
            {
                "username": "safes_student3",
                "password": "student123",
                "first_name": "Ana",
                "last_name": "Reyes",
                "email": "ana.reyes@student.edu",
                "student_id": f"{school_year.split('-')[0][-2:]}-BSAF-003",
                "course": courses.filter(code="BSAF").first() or courses[0],
                "year_level": 2,
                "contact_number": "9510440202"
            }
        ]
        
        # Get all offices
        all_offices = Office.objects.all()
        if not all_offices.exists():
            self.stdout.write(self.style.ERROR("No offices found. Please run base_populate first."))
            return
        
        # Get staff members to use as reviewers
        staff_members = {}
        for office in all_offices:
            staff = Staff.objects.filter(office=office).first()
            if staff:
                staff_members[office.id] = staff
        
        # Create students and their clearances
        for student_data in students_data:
            # Create or get user
            user, created = User.objects.get_or_create(
                username=student_data["username"],
                defaults={
                    "first_name": student_data["first_name"],
                    "last_name": student_data["last_name"],
                    "email": student_data["email"],
                    "is_active": True
                }
            )
            
            if created:
                user.set_password(student_data["password"])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user: {user.get_full_name()}"))
            else:
                self.stdout.write(self.style.WARNING(f"User already exists: {user.get_full_name()}"))
            
            # Create or get student
            student, created = Student.objects.get_or_create(
                user=user,
                defaults={
                    "student_id": student_data["student_id"],
                    "course": student_data["course"],
                    "program_chair": program_chair,
                    "year_level": student_data["year_level"],
                    "contact_number": student_data["contact_number"],
                    "is_boarder": False,
                    "is_approved": True
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created student: {student.user.get_full_name()} ({student.student_id})"))
            else:
                self.stdout.write(self.style.WARNING(f"Student already exists: {student.user.get_full_name()} ({student.student_id})"))
                # Update student data
                student.course = student_data["course"]
                student.program_chair = program_chair
                student.year_level = student_data["year_level"]
                student.contact_number = student_data["contact_number"]
                student.is_approved = True
                student.save()
                self.stdout.write(self.style.SUCCESS(f"Updated student: {student.user.get_full_name()} ({student.student_id})"))
            
            # Create or get clearance
            clearance, created = Clearance.objects.get_or_create(
                student=student,
                school_year=school_year,
                semester=semester,
                defaults={
                    "is_cleared": True,
                    "cleared_date": timezone.now(),
                    "program_chair_approved": True
                }
            )
            
            if not created:
                # Update clearance to be cleared
                clearance.is_cleared = True
                clearance.cleared_date = timezone.now()
                clearance.program_chair_approved = True
                clearance.save()
                self.stdout.write(self.style.SUCCESS(f"Updated clearance for {student.user.get_full_name()}"))
                
                # Delete existing clearance requests to start fresh
                ClearanceRequest.objects.filter(clearance=clearance).delete()
            
            # Get required offices based on student's school
            required_offices = Office.objects.filter(
                Q(office_type='OTHER') |
                Q(office_type=student.course.dean.name.split()[0])  # First word of dean name (e.g., "SAFES" from "SAFES DEAN")
            )
            
            # Create approved clearance requests for each office
            for office in required_offices:
                reviewer = staff_members.get(office.id)
                
                request = ClearanceRequest.objects.create(
                    student=student,
                    office=office,
                    clearance=clearance,
                    school_year=school_year,
                    semester=semester,
                    status='approved',
                    request_date=timezone.now() - timezone.timedelta(days=7),
                    reviewed_date=timezone.now(),
                    reviewed_by=reviewer
                )
                
                self.stdout.write(self.style.SUCCESS(
                    f"Created approved clearance request for {student.user.get_full_name()} - {office.name}"
                ))
            
            self.stdout.write(self.style.SUCCESS(
                f"Completed clearance for {student.user.get_full_name()} - Ready for permit printing"
            ))
