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

from core.utils import send_sms

def test_twilio_sms():
    """Test the Twilio SMS functionality."""
    # The Philippines number to test with
    test_number = '+639510440202'

    # Test message
    test_message = "This is a test message from the Student Clearance System. Please ignore."

    logging.info(f"Testing SMS sending to {test_number}")

    # First try with test mode
    logging.info("Testing in TEST MODE...")
    success, result, details = send_sms(test_number, test_message, test_mode=True)

    if success:
        logging.info(f"Test mode successful: {result}")
        logging.info(f"Details: {details}")
    else:
        logging.error(f"Test mode failed: {result}")
        logging.error(f"Details: {details}")

    # Note about real sending
    logging.info("\nNote about REAL SMS sending:")
    logging.info("In a production environment with a paid Twilio account, you would be able to send real SMS messages.")
    logging.info("With a trial account, you may encounter geographic restrictions or need to verify recipient numbers.")
    logging.info("For testing purposes, use test_mode=True to simulate sending without making API calls.")

if __name__ == "__main__":
    test_twilio_sms()
