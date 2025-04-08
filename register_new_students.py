import os
import django
import logging
import sys
import random
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clearance.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Student, Course, Dean

def register_students(num_students=5):
    """
    Register new students with pending approval status.
    All students will have the same contact number.
    """
    # Contact number to use for all students
    contact_number = '+639674703940'
    
    # Get all available courses
    courses = Course.objects.all()
    if not courses:
        logging.error("No courses found in the database. Please add courses first.")
        return
    
    # First names and last names for generating random student names
    first_names = [
        "Juan", "Maria", "Pedro", "Ana", "Carlos", "Sofia", "Luis", "Gabriela", 
        "Antonio", "Isabella", "Miguel", "Carmen", "Jose", "Elena", "Francisco", "Rosa"
    ]
    
    last_names = [
        "Garcia", "Santos", "Rodriguez", "Reyes", "Gonzalez", "Diaz", "Cruz", 
        "Fernandez", "Lopez", "Perez", "Torres", "Ramos", "Flores", "Mendoza"
    ]
    
    # Year levels
    year_levels = [1, 2, 3, 4]
    
    # Current year for student ID
    current_year = datetime.now().year % 100  # Get last 2 digits of year
    
    # Register students
    registered_count = 0
    for i in range(num_students):
        # Generate random student details
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(100, 999)}@example.com"
        username = f"{first_name.lower()}{last_name.lower()}{random.randint(10, 99)}"
        
        # Generate student ID: YY-FFLL-NNNN (year-firstlast-number)
        first_two_chars = first_name[:2].upper()
        last_two_chars = last_name[:2].upper()
        random_number = random.randint(1000, 9999)
        student_id = f"{current_year}-{first_two_chars}{last_two_chars}-{random_number}"
        
        # Select random course and year level
        course = random.choice(courses)
        year_level = random.choice(year_levels)
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password="password123",  # Default password
                first_name=first_name,
                last_name=last_name,
                is_active=False  # Not active until approved
            )
            
            # Create student
            student = Student.objects.create(
                user=user,
                student_id=student_id,
                course=course,
                year_level=year_level,
                contact_number=contact_number,
                is_approved=False
            )
            
            logging.info(f"Registered student: {student_id} - {first_name} {last_name} ({email}) - {course.code} Year {year_level}")
            registered_count += 1
            
        except Exception as e:
            logging.error(f"Error registering student {first_name} {last_name}: {str(e)}")
    
    logging.info(f"Successfully registered {registered_count} students with contact number {contact_number}")

if __name__ == "__main__":
    # Register 5 new students by default
    register_students(5)
