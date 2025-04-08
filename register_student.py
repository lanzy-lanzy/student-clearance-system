import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clearance_system.settings')
django.setup()

from core.models import Course, Student
from django.contrib.auth.models import User
import random
import string
from django.utils.text import slugify
from django.db import transaction

def generate_student_id(first_name, last_name, year_level):
    """Generate a unique student ID based on name and year level"""
    # Get current year last two digits
    import datetime
    year = datetime.datetime.now().year % 100
    
    # Create base student ID: YY-FFLL-XXXX
    first_chars = slugify(first_name)[:2].upper()
    last_chars = slugify(last_name)[:2].upper()
    random_digits = ''.join(random.choices(string.digits, k=4))
    
    student_id = f"{year}-{first_chars}{last_chars}-{random_digits}"
    
    # Check if this ID already exists, if so, generate a new one
    while Student.objects.filter(student_id=student_id).exists():
        random_digits = ''.join(random.choices(string.digits, k=4))
        student_id = f"{year}-{first_chars}{last_chars}-{random_digits}"
        
    return student_id

def generate_username(first_name, last_name):
    """Generate a unique username based on first and last name"""
    base_username = f"{slugify(first_name)}.{slugify(last_name)}"
    username = base_username
    counter = 1
    
    # Check if username exists, if so add a number
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
        
    return username

def generate_password(length=10):
    """Generate a random password"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))

def format_contact_number(contact_number):
    """Format contact number to E.164 format"""
    if not contact_number:
        return None
        
    if not contact_number.startswith('+'):
        if contact_number.startswith('0'):
            contact_number = '+63' + contact_number[1:]
        elif contact_number.startswith('63'):
            contact_number = '+' + contact_number
        else:
            contact_number = '+63' + contact_number
            
    return contact_number

def register_student(first_name, last_name, email, contact_number, course_code, 
                    year_level, is_boarder=False, password=None, approved=False):
    """Register a new student with the provided details"""
    
    # Validate course exists
    try:
        course = Course.objects.get(code=course_code)
    except Course.DoesNotExist:
        print(f"Error: Course with code '{course_code}' does not exist")
        print("Available courses:")
        for c in Course.objects.all():
            print(f"  - {c.code}: {c.name}")
        return None
    
    # Format contact number
    contact_number = format_contact_number(contact_number)
    
    # Generate username, password, and student ID
    username = generate_username(first_name, last_name)
    if not password:
        password = generate_password()
    student_id = generate_student_id(first_name, last_name, year_level)
    
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
            
            print(f"Successfully registered student: {student}")
            print(f"Username: {username}")
            print(f"Password: {password}")
            print(f"Student ID: {student_id}")
            print(f"Contact Number: {contact_number}")
            print(f"Status: {'Approved' if approved else 'Pending approval'}")
            
            return student
            
    except Exception as e:
        print(f"Error registering student: {str(e)}")
        return None

if __name__ == "__main__":
    # Example usage
    register_student(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        contact_number="639510440202",  # The number provided
        course_code="BSCS",  # Replace with an actual course code from your database
        year_level=2,
        is_boarder=True,
        approved=True
    )
