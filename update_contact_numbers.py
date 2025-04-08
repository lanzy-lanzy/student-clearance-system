import os
import django
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clearance.settings')
django.setup()

from core.models import Student
from django.contrib.auth.models import User

def update_pending_student_numbers():
    """Update the contact numbers of all pending students to the new number."""
    # New contact number to use
    new_contact_number = '+639674703940'
    
    # Get all pending students
    pending_students = Student.objects.filter(is_approved=False)
    
    logging.info(f"Found {pending_students.count()} pending students")
    
    # Update their contact numbers
    updated_count = 0
    for student in pending_students:
        old_number = student.contact_number
        student.contact_number = new_contact_number
        student.save()
        updated_count += 1
        logging.info(f"Updated student {student.student_id} ({student.user.get_full_name()}) contact number from {old_number} to {new_contact_number}")
    
    logging.info(f"Updated {updated_count} students to use contact number {new_contact_number}")

if __name__ == "__main__":
    update_pending_student_numbers()
