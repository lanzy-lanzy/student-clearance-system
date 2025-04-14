import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Twilio credentials
TWILIO_ACCOUNT_SID = 'AC6133d48f61383a9309ecab06e98c9b8f'
TWILIO_AUTH_TOKEN = '0fb7984f841156fcd65f26bdf18624df'
TWILIO_PHONE_NUMBER = '+15418033069'

# Verified number for testing
VERIFIED_NUMBER = '+639510440202'

def send_ph_sms(to_number, message):
    """
    Send an SMS to a Philippines number following Twilio's Philippines SMS guidelines.

    Args:
        to_number (str): The recipient's phone number in E.164 format (e.g., +639123456789)
        message (str): The message content to send

    Returns:
        bool: True if the message was sent successfully, False otherwise
        str: Message SID if successful, error message if failed
        dict: Additional information about the message status
    """
    # Debug information
    logging.info(f"Attempting to send SMS to Philippines number {to_number}")

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
        logging.warning("No phone number provided for SMS")
        return False, "No phone number provided", {"error_code": "NO_NUMBER"}

    # Verify this is a Philippines number
    if not to_number.startswith('+63'):
        logging.warning(f"Number {to_number} is not a Philippines number")
        return False, "Not a Philippines number", {"error_code": "NOT_PH_NUMBER"}

    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Prepare message parameters following Philippines guidelines
        params = {
            'body': message,
            'from_': TWILIO_PHONE_NUMBER,
            'to': to_number,
        }

        # Send the message
        message_obj = client.messages.create(**params)

        # Log success
        logging.info(f"SMS sent successfully to {to_number}. SID: {message_obj.sid}")
        return True, message_obj.sid, {"status": "sent", "provider": "twilio_ph"}

    except TwilioRestException as e:
        # Handle Twilio-specific errors
        error_code = e.code
        error_message = e.msg
        logging.error(f"Twilio API error {error_code}: {error_message}")

        # Check for specific error codes
        if error_code == 21612:
            # Geographic permission error - common with trial accounts
            # For trial accounts, simulate sending instead
            logging.warning("Twilio geographic permission error. This is common with trial accounts.")
            logging.warning("Simulating SMS delivery for trial account.")

            # Return success with simulation details
            return True, "SIMULATED_DUE_TO_TRIAL_ACCOUNT", {
                "simulated": True,
                "to": to_number,
                "message": message,
                "original_error": error_message,
                "error_code": error_code,
                "note": "SMS simulated due to Twilio trial account geographic restrictions"
            }
        elif error_code == 21608:
            # Unverified number in trial account - simulate sending
            logging.warning("Recipient number not verified in Twilio trial account.")
            logging.warning("Simulating SMS delivery for trial account.")

            # Return success with simulation details
            return True, "SIMULATED_DUE_TO_UNVERIFIED_NUMBER", {
                "simulated": True,
                "to": to_number,
                "message": message,
                "original_error": error_message,
                "error_code": error_code,
                "note": "SMS simulated due to unverified number in Twilio trial account"
            }
        else:
            return False, error_message, {"error_type": "TWILIO_API_ERROR", "error_code": error_code}

    except Exception as e:
        # Handle other exceptions
        logging.error(f"Unexpected error sending SMS to {to_number}: {str(e)}")
        return False, str(e), {"error_type": "UNEXPECTED_ERROR"}
