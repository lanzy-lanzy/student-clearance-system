import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Twilio credentials
TWILIO_ACCOUNT_SID = 'AC6133d48f61383a9309ecab06e98c9b8f'
TWILIO_AUTH_TOKEN = '0fb7984f841156fcd65f26bdf18624df'

# Verified number for testing
VERIFIED_NUMBER = '+639510440202'

def send_whatsapp_message(to_number, message):
    """
    Send a WhatsApp message to a verified phone number using Twilio WhatsApp API.
    
    Args:
        to_number (str): The recipient's phone number in E.164 format (e.g., +639123456789)
        message (str): The message content to send
        
    Returns:
        bool: True if the message was sent successfully, False otherwise
        str: Message SID if successful, error message if failed
        dict: Additional information about the message status
    """
    # Debug information
    logging.info(f"Attempting to send WhatsApp message to verified number {to_number}")
    
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
        logging.warning("No phone number provided for WhatsApp message")
        return False, "No phone number provided", {"error_code": "NO_NUMBER"}
    
    # Verify this is the verified number
    if to_number != VERIFIED_NUMBER:
        logging.warning(f"Number {to_number} is not the verified number {VERIFIED_NUMBER}")
        return False, "Not a verified number", {"error_code": "NOT_VERIFIED"}
    
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Send the WhatsApp message
        # Note: The 'from' number must be a Twilio WhatsApp-enabled number
        message_obj = client.messages.create(
            body=message,
            from_='whatsapp:+14155238886',  # Twilio's WhatsApp sandbox number
            to=f'whatsapp:{to_number}'
        )
        
        # Log success
        logging.info(f"WhatsApp message sent successfully to {to_number}. SID: {message_obj.sid}")
        return True, message_obj.sid, {"status": "sent", "provider": "twilio_whatsapp"}
        
    except TwilioRestException as e:
        # Handle Twilio-specific errors
        error_code = e.code
        error_message = e.msg
        logging.error(f"Twilio API error {error_code}: {error_message}")
        return False, error_message, {"error_type": "TWILIO_API_ERROR", "error_code": error_code}
        
    except Exception as e:
        # Handle other exceptions
        logging.error(f"Unexpected error sending WhatsApp message to {to_number}: {str(e)}")
        return False, str(e), {"error_type": "UNEXPECTED_ERROR"}
