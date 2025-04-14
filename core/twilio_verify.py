import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Twilio credentials
TWILIO_ACCOUNT_SID = 'AC6133d48f61383a9309ecab06e98c9b8f'
TWILIO_AUTH_TOKEN = '0fb7984f841156fcd65f26bdf18624df'
VERIFY_SERVICE_SID = 'VA28508c25ebbc58bccd88d260438c0712'  # The service SID created in our test

def send_verification_message(to_number, message=None):
    """
    Send a verification code to a verified phone number using Twilio Verify API.
    Note: The Verify API sends a standard verification message with a code, not a custom message.
    The message parameter is ignored but kept for compatibility with the send_sms function signature.

    Args:
        to_number (str): The recipient's phone number in E.164 format (e.g., +639123456789)
        message (str, optional): Ignored. The Verify API sends a standard message.

    Returns:
        bool: True if the verification was sent successfully, False otherwise
        str: Verification SID if successful, error message if failed
        dict: Additional information about the verification status
    """
    # Debug information
    logging.info(f"Attempting to send verification message to {to_number}")

    # Format the phone number if needed
    original_number = to_number
    if to_number:
        # Ensure the number has a '+' prefix for Twilio
        if not to_number.startswith('+'):
            # If number starts with 0, assume it's a Philippines number and add +63 prefix
            if to_number.startswith('0'):
                to_number = '+63' + to_number[1:]
            # If it doesn't have country code, assume Philippines (+63)
            elif len(to_number) <= 10:
                to_number = '+63' + to_number
            else:
                to_number = '+' + to_number

        logging.info(f"Formatted phone number from {original_number} to {to_number}")
    else:
        # No phone number provided
        logging.warning("No phone number provided for verification message")
        return False, "No phone number provided", {"error_code": "NO_NUMBER"}

    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Send the verification
        verification = client.verify \
            .v2 \
            .services(VERIFY_SERVICE_SID) \
            .verifications \
            .create(to=to_number, channel='sms')

        # Log success
        logging.info(f"Verification code sent successfully to {to_number}. SID: {verification.sid}")
        logging.info(f"Note: This is a standard verification message with a code, not a custom message.")
        return True, verification.sid, {"status": "sent", "provider": "twilio_verify", "note": "Standard verification code sent"}

    except TwilioRestException as e:
        # Handle Twilio-specific errors
        error_code = e.code
        error_message = e.msg
        logging.error(f"Twilio Verify API error {error_code}: {error_message}")
        return False, error_message, {"error_type": "TWILIO_API_ERROR", "error_code": error_code}

    except Exception as e:
        # Handle other exceptions
        logging.error(f"Unexpected error sending verification message to {to_number}: {str(e)}")
        return False, str(e), {"error_type": "UNEXPECTED_ERROR"}
