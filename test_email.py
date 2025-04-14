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

from core.email_utils import send_email

# Test the send_email function
success, result, details = send_email(
    'bigbren480@gmail.com',  # Replace with your email for testing
    'Test Email from Student Clearance System',
    'This is a test email from the Student Clearance System.',
    '<h1>Test Email</h1><p>This is a test email from the Student Clearance System.</p>'
)

print(f"Success: {success}")
print(f"Result: {result}")
print(f"Details: {details}")
