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

def send_verification_code():
    """Send a verification code to the verified number using Twilio Verify API."""
    # Twilio credentials
    account_sid = 'AC6133d48f61383a9309ecab06e98c9b8f'
    auth_token = '0fb7984f841156fcd65f26bdf18624df'
    
    # Verified recipient number
    verified_number = '+639510440202'
    
    logging.info(f"Sending verification code to {verified_number}")
    
    try:
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # First, check if we have a Verify service already
        services = client.verify.v2.services.list(limit=20)
        
        # Use existing service or create a new one
        if services:
            service_sid = services[0].sid
            logging.info(f"Using existing Verify service: {service_sid}")
        else:
            # Create a new Verify service
            service = client.verify.v2.services.create(
                friendly_name='Student Clearance System'
            )
            service_sid = service.sid
            logging.info(f"Created new Verify service: {service_sid}")
        
        # Send verification
        verification = client.verify \
            .v2 \
            .services(service_sid) \
            .verifications \
            .create(to=verified_number, channel='sms')
        
        logging.info(f"Verification status: {verification.status}")
        logging.info(f"A verification code has been sent to {verified_number}")
        logging.info(f"Please check your phone and enter the code when prompted")
        
        # Ask for verification code
        code = input("Enter the verification code you received: ")
        
        # Check verification code
        verification_check = client.verify \
            .v2 \
            .services(service_sid) \
            .verification_checks \
            .create(to=verified_number, code=code)
        
        logging.info(f"Verification check status: {verification_check.status}")
        
        if verification_check.status == 'approved':
            return True, "Verification successful"
        else:
            return False, f"Verification failed with status: {verification_check.status}"
        
    except Exception as e:
        # Log error
        logging.error(f"Failed to send verification: {str(e)}")
        return False, str(e)

if __name__ == "__main__":
    success, result = send_verification_code()
    
    if success:
        logging.info("Verification completed successfully!")
    else:
        logging.error(f"Verification failed: {result}")
