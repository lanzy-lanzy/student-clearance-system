import os
import sys
import django
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clearance.settings')
django.setup()

from core.management.commands.register_student import Command

# Sample data for student registration
first_names = [
    "Maria", "Juan", "Ana", "Carlos", "Sofia",
    "Miguel", "Gabriela", "Jose", "Isabella", "Antonio",
    "Elena", "Luis", "Carmen", "Pedro", "Rosa"
]

last_names = [
    "Santos", "Reyes", "Cruz", "Garcia", "Fernandez",
    "Lopez", "Martinez", "Gonzalez", "Rodriguez", "Torres",
    "Perez", "Ramos", "Flores", "Diaz", "Mendoza"
]

courses = ["BSCS", "BSA", "BSED", "BSN", "BEED", "BSAF", "BSCrim"]

# Email domains
email_domains = ["gmail.com", "yahoo.com", "outlook.com", "mail.com", "example.com"]

# Fixed contact number (Philippines)
contact_number = "9510440202"

def generate_email(first_name, last_name):
    domain = random.choice(email_domains)
    return f"{first_name.lower()}.{last_name.lower()}@{domain}"

def main():
    command = Command()

    print("Registering 10 pending students...")

    for i in range(10):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = generate_email(first_name, last_name)
        # Use the fixed contact number for all students
        course_code = random.choice(courses)
        year_level = random.randint(1, 4)
        is_boarder = random.choice([True, False])

        # Use the command's handle method to register the student
        options = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'contact_number': contact_number,
            'course_code': course_code,
            'year_level': year_level,
            'is_boarder': is_boarder,
            'password': None,  # Will be auto-generated
            'approved': False  # All students will be pending
        }

        try:
            command.handle(**options)
            print(f"Registered student #{i+1}: {first_name} {last_name}")
        except Exception as e:
            print(f"Error registering student #{i+1}: {str(e)}")

    print("\nAll students registered successfully!")
    print("You can now check the pending approvals in the admin panel.")

if __name__ == "__main__":
    main()
