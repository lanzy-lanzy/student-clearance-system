import random
import string
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Student, Course
from django.db import transaction
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Register a new student with the provided details'

    def add_arguments(self, parser):
        parser.add_argument('--first_name', type=str, required=True, help='First name of the student')
        parser.add_argument('--last_name', type=str, required=True, help='Last name of the student')
        parser.add_argument('--email', type=str, required=True, help='Email address of the student')
        parser.add_argument('--contact_number', type=str, default='639510440202', help='Contact number of the student')
        parser.add_argument('--course_code', type=str, required=True, help='Course code (must exist in the database)')
        parser.add_argument('--year_level', type=int, required=True, choices=[1, 2, 3, 4, 5], help='Year level (1-5)')
        parser.add_argument('--is_boarder', action='store_true', help='Whether the student is a boarder')
        parser.add_argument('--password', type=str, help='Password for the student account (optional, will be generated if not provided)')
        parser.add_argument('--approved', action='store_true', help='Whether to automatically approve the student')

    def generate_student_id(self, first_name, last_name, year_level):
        """Generate a unique student ID based on name and year level"""
        # Get current year last two digits
        import datetime
        year = datetime.datetime.now().year % 100
        
        # Create base student ID: YY-FFLL-XXXX where:
        # YY = last two digits of current year
        # FF = first two letters of first name
        # LL = first two letters of last name
        # XXXX = random 4-digit number
        first_chars = slugify(first_name)[:2].upper()
        last_chars = slugify(last_name)[:2].upper()
        random_digits = ''.join(random.choices(string.digits, k=4))
        
        student_id = f"{year}-{first_chars}{last_chars}-{random_digits}"
        
        # Check if this ID already exists, if so, generate a new one
        while Student.objects.filter(student_id=student_id).exists():
            random_digits = ''.join(random.choices(string.digits, k=4))
            student_id = f"{year}-{first_chars}{last_chars}-{random_digits}"
            
        return student_id

    def generate_username(self, first_name, last_name):
        """Generate a unique username based on first and last name"""
        base_username = f"{slugify(first_name)}.{slugify(last_name)}"
        username = base_username
        counter = 1
        
        # Check if username exists, if so add a number
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
            
        return username

    def generate_password(self, length=10):
        """Generate a random password"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*()"
        return ''.join(random.choice(chars) for _ in range(length))

    def handle(self, *args, **options):
        first_name = options['first_name']
        last_name = options['last_name']
        email = options['email']
        contact_number = options['contact_number']
        course_code = options['course_code']
        year_level = options['year_level']
        is_boarder = options['is_boarder']
        password = options['password'] or self.generate_password()
        approved = options['approved']
        
        # Validate course exists
        try:
            course = Course.objects.get(code=course_code)
        except Course.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Course with code '{course_code}' does not exist"))
            self.stdout.write(self.style.WARNING("Available courses:"))
            for c in Course.objects.all():
                self.stdout.write(f"  - {c.code}: {c.name}")
            return
        
        # Format contact number if needed
        if contact_number and not contact_number.startswith('+'):
            if contact_number.startswith('0'):
                contact_number = '+63' + contact_number[1:]
            elif contact_number.startswith('63'):
                contact_number = '+' + contact_number
            else:
                contact_number = '+63' + contact_number
        
        # Generate username and student ID
        username = self.generate_username(first_name, last_name)
        student_id = self.generate_student_id(first_name, last_name, year_level)
        
        try:
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=approved  # Only activate if approved
                )
                
                # Create student
                student = Student.objects.create(
                    user=user,
                    student_id=student_id,
                    course=course,
                    year_level=year_level,
                    contact_number=contact_number,
                    is_boarder=is_boarder,
                    is_approved=approved
                )
                
                self.stdout.write(self.style.SUCCESS(f"Successfully registered student: {student}"))
                self.stdout.write(f"Username: {username}")
                self.stdout.write(f"Password: {password}")
                self.stdout.write(f"Student ID: {student_id}")
                self.stdout.write(f"Contact Number: {contact_number}")
                self.stdout.write(f"Status: {'Approved' if approved else 'Pending approval'}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error registering student: {str(e)}"))
