import os
import django
import logging
import sys
import time
import socket
import ssl
from smtplib import SMTPException

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

# Test network connectivity to the SMTP server
logger.info("Testing network connectivity to SMTP server...")
try:
    # Create a socket connection to test connectivity
    sock = socket.create_connection((settings.EMAIL_HOST, settings.EMAIL_PORT), timeout=10)
    sock.close()
    logger.info(f"Successfully connected to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
except Exception as e:
    logger.error(f"Failed to connect to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}: {str(e)}")
    logger.error("This indicates a network connectivity issue or firewall blocking the connection.")

# Test the send_email function
logger.info("Sending test email...")
try:
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
except (socket.error, ssl.SSLError, SMTPException) as e:
    error_type = type(e).__name__
    logger.error(f"Email sending failed with {error_type}: {str(e)}")

    # Log more detailed information about the error
    if isinstance(e, socket.error):
        logger.error(f"Socket error details: Error code: {e.errno if hasattr(e, 'errno') else 'N/A'}")
        logger.error(f"Socket error message: {e.strerror if hasattr(e, 'strerror') else 'N/A'}")
    elif isinstance(e, ssl.SSLError):
        logger.error(f"SSL error details: {e.reason if hasattr(e, 'reason') else 'N/A'}")
    elif isinstance(e, SMTPException):
        logger.error(f"SMTP error details: {e.smtp_code if hasattr(e, 'smtp_code') else 'N/A'} - {e.smtp_error if hasattr(e, 'smtp_error') else 'N/A'}")
except Exception as e:
    logger.error(f"Unexpected error during email test: {type(e).__name__} - {str(e)}")

print("\nTest completed. Check the logs above for results.")
