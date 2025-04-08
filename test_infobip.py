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

def test_infobip_integration():
    """Test the Infobip integration by sending a test SMS."""
    # The Philippines number to test with
    test_number = '+639510440202'
    
    # Test message
    test_message = "This is a test message from the Clearance System using Infobip. Please ignore."
    
    logging.info(f"Testing SMS sending to {test_number}")
    
    # First try with test mode
    logging.info("Testing in TEST MODE...")
    success, result, details = send_sms(test_number, test_message, test_mode=True)
    
    if success:
        logging.info(f"Test mode successful: {result}")
    else:
        logging.error(f"Test mode failed: {result}")
        logging.error(f"Details: {details}")
    
    # Now try with real sending
    logging.info("\nTesting REAL SMS sending via Infobip...")
    success, result, details = send_sms(test_number, test_message, test_mode=False)
    
    if success:
        logging.info(f"Real SMS sent successfully! ID: {result}")
        logging.info(f"Response details: {details}")
    else:
        logging.error(f"Failed to send real SMS: {result}")
        logging.error(f"Error details: {details}")

if __name__ == "__main__":
    test_infobip_integration()
