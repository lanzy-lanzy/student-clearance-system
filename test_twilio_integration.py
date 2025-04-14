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

from core.utils import send_sms, send_sms_twilio, send_sms_infobip

def test_twilio_integration():
    """Test the Twilio integration by sending a test SMS."""
    # The Philippines number to test with
    test_number = '+639510440202'

    # Test message
    test_message = "This is a test message from the Clearance System using Twilio. Please ignore."

    logging.info(f"Testing SMS sending to {test_number}")

    # Test in test mode only to avoid API errors
    logging.info("Testing in TEST MODE...")
    success, result, details = send_sms_twilio(test_number, test_message, test_mode=True)

    if success:
        logging.info(f"Test mode successful: {result}")
        logging.info(f"Details: {details}")
    else:
        logging.error(f"Test mode failed: {result}")
        logging.error(f"Details: {details}")

    # Note about real sending
    logging.info("\nNote: Real SMS sending via Twilio is not tested to avoid geographic restriction errors.")
    logging.info("In a production environment, you would need to upgrade your Twilio account or use verified numbers.")

def test_combined_sms_function():
    """Test the combined SMS function that tries Twilio first, then Infobip."""
    # The Philippines number to test with
    test_number = '+639510440202'

    # Test message
    test_message = "This is a test message from the Clearance System using the combined SMS function. Please ignore."

    logging.info(f"Testing combined SMS sending to {test_number}")

    # First try with test mode
    logging.info("Testing in TEST MODE...")
    success, result, details = send_sms(test_number, test_message, test_mode=True)

    if success:
        logging.info(f"Test mode successful: {result}")
        logging.info(f"Details: {details}")
    else:
        logging.error(f"Test mode failed: {result}")
        logging.error(f"Details: {details}")

    # Now try with real sending
    logging.info("\nTesting REAL SMS sending via combined function...")
    success, result, details = send_sms(test_number, test_message, test_mode=False)

    if success:
        logging.info(f"Real SMS sent successfully! ID: {result}")
        logging.info(f"Response details: {details}")
    else:
        logging.error(f"Failed to send real SMS: {result}")
        logging.error(f"Error details: {details}")

if __name__ == "__main__":
    # First test direct Twilio integration
    logging.info("=== TESTING DIRECT TWILIO INTEGRATION ===")
    test_twilio_integration()

    # Then test the combined SMS function
    logging.info("\n\n=== TESTING COMBINED SMS FUNCTION ===")
    test_combined_sms_function()
