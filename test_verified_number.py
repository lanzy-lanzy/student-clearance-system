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

from twilio.rest import Client

def send_test_sms_to_verified_number():
    """Send a test SMS directly to the verified number using Twilio."""
    # Twilio credentials
    account_sid = 'AC6133d48f61383a9309ecab06e98c9b8f'
    auth_token = '0fb7984f841156fcd65f26bdf18624df'
    twilio_number = '+15418033069'
    
    # Verified recipient number
    verified_number = '+639510440202'
    
    # Test message
    test_message = "This is a test message from the Student Clearance System. Sent directly to verified number."
    
    logging.info(f"Sending direct SMS to verified number {verified_number}")
    
    try:
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send the message
        message = client.messages.create(
            body=test_message,
            from_=twilio_number,
            to=verified_number
        )
        
        # Log success
        logging.info(f"SMS sent successfully! SID: {message.sid}")
        logging.info(f"Message status: {message.status}")
        
        return True, message.sid
    except Exception as e:
        # Log error
        logging.error(f"Failed to send SMS: {str(e)}")
        return False, str(e)

if __name__ == "__main__":
    success, result = send_test_sms_to_verified_number()
    
    if success:
        logging.info("Test completed successfully!")
    else:
        logging.error(f"Test failed: {result}")
