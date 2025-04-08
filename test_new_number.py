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

def test_infobip_with_new_number():
    """Test the Infobip integration with the new phone number."""
    # The new Philippines number to test with
    test_number = '+639674703940'
    
    # Test message
    test_message = "This is a test message from the Clearance System using Infobip with the new number. Please ignore."
    
    logging.info(f"Testing SMS sending to {test_number}")
    
    # Send the SMS
    success, result, details = send_sms(test_number, test_message, test_mode=False)
    
    if success:
        logging.info(f"SMS sent successfully! ID: {result}")
        logging.info(f"Response details: {details}")
    else:
        logging.error(f"Failed to send SMS: {result}")
        logging.error(f"Error details: {details}")

if __name__ == "__main__":
    test_infobip_with_new_number()
