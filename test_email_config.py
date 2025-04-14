import os
import django
import logging
import sys
import time

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
from django.conf import settings

# Log the email configuration
logger = logging.getLogger(__name__)
logger.info(f"Email Configuration:")
logger.info(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
logger.info(f"EMAIL_HOST: {settings.EMAIL_HOST}")
logger.info(f"EMAIL_PORT: {settings.EMAIL_PORT}")
logger.info(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
logger.info(f"EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
logger.info(f"EMAIL_TIMEOUT: {settings.EMAIL_TIMEOUT}")
logger.info(f"EMAIL_MAX_RETRIES: {getattr(settings, 'EMAIL_MAX_RETRIES', 3)}")
logger.info(f"EMAIL_RETRY_DELAY: {getattr(settings, 'EMAIL_RETRY_DELAY', 5)}")
logger.info(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# Test the send_email function
logger.info("Sending test email...")
success, result, details = send_email(
    'balolaoapriljane11@gmail.com',  # Use the email from the error log
    'Test Email from Student Clearance System',
    'This is a test email from the Student Clearance System.',
    '<h1>Test Email</h1><p>This is a test email from the Student Clearance System.</p>'
)

# Log the result
if success:
    logger.info(f"Email sent successfully: {result}")
    logger.info(f"Details: {details}")
else:
    logger.error(f"Email sending failed: {result}")
    logger.error(f"Details: {details}")

print("\nTest completed. Check the logs above for results.")
