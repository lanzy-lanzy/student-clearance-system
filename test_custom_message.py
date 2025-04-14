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

def test_custom_message():
    """Test sending a custom message to the verified number."""
    # The verified Philippines number
    verified_number = '+639510440202'
    
    # Get custom message from user
    print("\n=== Send Custom Message to Verified Number ===")
    print(f"This will send a real SMS to your verified number: {verified_number}")
    message = input("Enter your custom message: ")
    
    if not message:
        print("Message cannot be empty. Using default message.")
        message = "This is a test message from the Student Clearance System."
    
    logging.info(f"Sending custom message to {verified_number}: \"{message}\"")
    
    # Send the SMS
    success, result, details = send_sms(verified_number, message, test_mode=False)
    
    if success:
        logging.info(f"Custom message sent successfully! ID: {result}")
        logging.info(f"Response details: {details}")
    else:
        logging.error(f"Failed to send custom message: {result}")
        logging.error(f"Error details: {details}")

if __name__ == "__main__":
    test_custom_message()
