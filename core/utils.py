import logging
import http.client
import json
import re
from django.utils import timezone

# Import Twilio for SMS functionality
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logging.warning("Twilio library not available. SMS functionality will not work.")

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor

# Twilio credentials - should be loaded from environment variables in production
TWILIO_ACCOUNT_SID = 'AC6133d48f61383a9309ecab06e98c9b8f'  # Replace with environment variable in production
TWILIO_AUTH_TOKEN = '0fb7984f841156fcd65f26bdf18624df'  # Replace with environment variable in production
TWILIO_PHONE_NUMBER = '+15418033069'  # Replace with environment variable in production

# Infobip credentials - should be loaded from environment variables in production
INFOBIP_API_HOST = 'ypejm9.api.infobip.com'  # Replace with environment variable in production
INFOBIP_API_KEY = 'a3169c60a19754c3df10cf1dd3de3f94-191444f9-cc43-426f-811e-84af9998698f'  # Replace with environment variable in production
INFOBIP_SENDER = '447491163443'  # Replace with environment variable in production

# For production, use environment variables:
# import os
# TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
# TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
# TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
# INFOBIP_API_HOST = os.environ.get('INFOBIP_API_HOST')
# INFOBIP_API_KEY = os.environ.get('INFOBIP_API_KEY')
# INFOBIP_SENDER = os.environ.get('INFOBIP_SENDER')

def generate_pdf_report(response, data):
    # Create document
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []

    # Define emerald theme colors
    emerald_dark = HexColor('#047857')  # Emerald-700
    emerald_light = HexColor('#10B981')  # Emerald-500

    # Custom styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        textColor=emerald_dark,
        fontSize=24,
        spaceAfter=30
    )

    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        textColor=emerald_dark,
        fontSize=16,
        spaceAfter=12
    )

    # Add title
    elements.append(Paragraph("Clearance Status Report", title_style))
    elements.append(Spacer(1, 20))

    # Statistics Table
    stats_data = [
        ['Total Students', str(data['total_students'])],
        ['Cleared Students', str(data['cleared_students'])],
        ['Pending Clearance', str(data['pending_clearance'])]
    ]

    stats_table = Table(stats_data, colWidths=[300, 200])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#ECFDF5')),  # Emerald-50
        ('TEXTCOLOR', (0, 0), (-1, -1), emerald_dark),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, emerald_light)
    ]))

    elements.append(stats_table)
    elements.append(Spacer(1, 30))

    # Add detailed breakdown section
    elements.append(Paragraph("Detailed Breakdown", header_style))
    elements.append(Spacer(1, 10))

    # Create detailed table
    if data.get('detailed_data'):
        detailed_headers = [['Department', 'Pending', 'Approved', 'Denied']]
        detailed_data = detailed_headers + data['detailed_data']

        detailed_table = Table(detailed_data, colWidths=[200, 100, 100, 100])
        detailed_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), emerald_dark),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F0FDF4')),  # Emerald-50
            ('GRID', (0, 0), (-1, -1), 1, emerald_light)
        ]))

        elements.append(detailed_table)

    # Build PDF
    doc.build(elements)

def send_sms_infobip(to_number, message, test_mode=False):
    """
    Send an SMS message using Infobip API.

    Args:
        to_number (str): The recipient's phone number (e.g., 639123456789)
        message (str): The message content to send
        test_mode (bool): If True, will simulate sending without actually calling Infobip API

    Returns:
        bool: True if the message was sent successfully, False otherwise
        str: Message ID if successful, error message if failed
        dict: Additional information about the message status
    """
    # Debug information
    logging.info(f"Attempting to send SMS via Infobip - To: {to_number}, Test Mode: {test_mode}")

    # Format the phone number if needed
    original_number = to_number
    if to_number:
        # Remove any '+' prefix as Infobip doesn't need it
        if to_number.startswith('+'):
            to_number = to_number[1:]

        # If number starts with 0, assume it's a Philippines number and add 63 prefix
        if to_number.startswith('0'):
            to_number = '63' + to_number[1:]

        # If it doesn't have country code and not starting with 0, assume Philippines (63)
        if len(to_number) <= 10 and not to_number.startswith('63'):
            to_number = '63' + to_number

        logging.info(f"Formatted phone number from {original_number} to {to_number}")
    else:
        # No phone number provided
        logging.warning("No phone number provided for SMS")
        return False, "No phone number provided", {"error_code": "NO_NUMBER"}

    # Test mode - simulate sending without calling Infobip API
    if test_mode:
        logging.info(f"[TEST MODE] SMS would be sent to {to_number} with message: {message}")
        return True, "TEST_MODE_ID", {"test_mode": True, "to": to_number, "message": message}

    try:
        # Set up the connection to Infobip API
        conn = http.client.HTTPSConnection(INFOBIP_API_HOST)

        # Prepare the payload
        payload = json.dumps({
            "messages": [
                {
                    "destinations": [{"to": to_number}],
                    "from": INFOBIP_SENDER,
                    "text": message
                }
            ]
        })

        # Set up the headers
        headers = {
            'Authorization': f'App {INFOBIP_API_KEY}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # Make the request
        logging.info(f"Sending SMS via Infobip from {INFOBIP_SENDER} to {to_number}...")
        conn.request("POST", "/sms/2/text/advanced", payload, headers)

        # Get the response
        res = conn.getresponse()
        data = res.read()
        response_data = json.loads(data.decode("utf-8"))

        # Check if the request was successful
        if res.status == 200:
            # Extract the message ID from the response
            message_id = response_data.get('messages', [{}])[0].get('messageId', 'UNKNOWN_ID')
            logging.info(f"SMS sent successfully via Infobip to {to_number}. ID: {message_id}")
            return True, message_id, {"status": "sent", "response": response_data}
        else:
            # Handle error response
            error_message = response_data.get('requestError', {}).get('serviceException', {}).get('text', 'Unknown error')
            logging.error(f"Infobip API error: {error_message}")
            return False, error_message, {"error_type": "API_ERROR", "response": response_data}

    except Exception as e:
        logging.error(f"Unexpected error sending SMS via Infobip to {to_number}: {str(e)}")
        return False, str(e), {"error_type": "UNEXPECTED_ERROR"}


def send_sms_twilio(to_number, message, test_mode=False):
    """
    Send an SMS message using Twilio API.

    Args:
        to_number (str): The recipient's phone number in E.164 format (e.g., +639123456789)
        message (str): The message content to send
        test_mode (bool): If True, will simulate sending without actually calling Twilio API

    Returns:
        bool: True if the message was sent successfully, False otherwise
        str: Message SID if successful, error message if failed
        dict: Additional information about the message status
    """
    # Debug information
    logging.info(f"Attempting to send SMS via Twilio - To: {to_number}, Test Mode: {test_mode}")

    # Check if Twilio is available
    if not TWILIO_AVAILABLE:
        logging.warning("Twilio library not available. Cannot send SMS via Twilio.")
        return False, "Twilio library not available", {"error_type": "LIBRARY_UNAVAILABLE"}

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

    # Test mode - simulate sending without calling Twilio API
    if test_mode:
        logging.info(f"[TEST MODE] SMS would be sent to {to_number} with message: {message}")
        return True, "TEST_MODE_SID", {"test_mode": True, "to": to_number, "message": message}

    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Send the message
        logging.info(f"Sending SMS via Twilio from {TWILIO_PHONE_NUMBER} to {to_number}...")
        message_obj = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )

        # Log success
        logging.info(f"SMS sent successfully via Twilio to {to_number}. SID: {message_obj.sid}")
        return True, message_obj.sid, {"status": "sent", "provider": "twilio"}

    except TwilioRestException as e:
        # Handle Twilio-specific errors
        error_code = e.code
        error_message = e.msg
        logging.error(f"Twilio API error {error_code}: {error_message}")

        # Check for specific error codes
        if error_code == 21612:
            # Geographic permission error
            logging.warning("Twilio geographic permission error. This is common with trial accounts.")
            return False, error_message, {"error_type": "GEOGRAPHIC_RESTRICTION", "error_code": error_code}
        elif error_code == 21608:
            # Unverified number in trial account
            logging.warning("Recipient number not verified in Twilio trial account.")
            return False, error_message, {"error_type": "UNVERIFIED_NUMBER", "error_code": error_code}
        else:
            return False, error_message, {"error_type": "TWILIO_API_ERROR", "error_code": error_code}

    except Exception as e:
        # Handle other exceptions
        logging.error(f"Unexpected error sending SMS via Twilio to {to_number}: {str(e)}")
        return False, str(e), {"error_type": "UNEXPECTED_ERROR"}


# Create a logger for this module
logger = logging.getLogger(__name__)

def validate_phone_number(phone_number):
    """Validate Philippine mobile number format."""
    if not phone_number:
        return False
    pattern = r'^\+639\d{9}$'
    return bool(re.match(pattern, str(phone_number)))

def format_phone_number(phone_number):
    """Format phone number to E.164 format."""
    if not phone_number:
        return None

    # Convert to string if it's not already
    phone_number = str(phone_number)

    # Remove any spaces, dashes, or parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone_number)

    # If number starts with 09, convert to +639
    if cleaned.startswith('09'):
        cleaned = '+63' + cleaned[1:]
    # If number starts with 639, add +
    elif cleaned.startswith('639'):
        cleaned = '+' + cleaned
    # If number doesn't start with +639, it's invalid
    elif not cleaned.startswith('+639'):
        return None

    return cleaned

def send_sms(to_number, message, test_mode=False):
    """Send SMS using Twilio.

    Args:
        to_number (str): The recipient's phone number in E.164 format (e.g., +639123456789)
        message (str): The message content to send
        test_mode (bool): If True, will simulate sending without actually calling the SMS API

    Returns:
        bool: True if the message was sent successfully, False otherwise
        str: Message ID if successful, error message if failed
        dict: Additional information about the message status
    """
    logger.info(f"Attempting to send SMS to: {to_number}, Test Mode: {test_mode}")

    if not to_number:
        logger.error("SMS sending failed: No phone number provided")
        return False, "No phone number provided", {"error_code": "NO_NUMBER"}

    # Test mode - simulate sending without calling Twilio API
    if test_mode:
        logger.info(f"[TEST MODE] SMS would be sent to {to_number} with message: {message}")
        return True, "TEST_MODE_SID", {"test_mode": True, "to": to_number, "message": message}

    # Format the phone number
    formatted_number = format_phone_number(to_number)
    if not formatted_number:
        logger.error(f"SMS sending failed: Could not format phone number: {to_number}")
        return False, "Invalid phone number format", {"error_code": "INVALID_FORMAT"}

    # Validate the phone number
    if not validate_phone_number(formatted_number):
        logger.error(f"SMS sending failed: Invalid phone number format: {formatted_number}")
        return False, "Invalid phone number format", {"error_code": "INVALID_FORMAT"}

    try:
        # Log Twilio credentials (without sensitive data)
        logger.info(f"Using Twilio number: {TWILIO_PHONE_NUMBER}")
        logger.info(f"Account SID length: {len(TWILIO_ACCOUNT_SID)}")

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Log the message details before sending
        logger.info(f"Sending SMS - To: {formatted_number}, From: {TWILIO_PHONE_NUMBER}, Message: {message[:50]}...")

        message_obj = client.messages.create(
            to=formatted_number,  # Make sure this is a string
            from_=TWILIO_PHONE_NUMBER,
            body=message
        )

        logger.info(f"SMS sent successfully to {formatted_number} - Message SID: {message_obj.sid}")
        return True, message_obj.sid, {"status": "sent", "provider": "twilio"}

    except TwilioRestException as e:
        # Handle Twilio-specific errors
        error_code = e.code
        error_message = e.msg
        logger.error(f"Twilio API error {error_code}: {error_message}")

        # Check for specific error codes
        if error_code == 21612:
            # Geographic permission error - common with trial accounts
            # For trial accounts, simulate sending instead
            logger.warning("Twilio geographic permission error. This is common with trial accounts.")
            logger.warning("Simulating SMS delivery for trial account.")

            # Return success with simulation details
            logger.info(f"SIMULATED SMS to {formatted_number}: '{message}'")
            return True, "SIMULATED_DUE_TO_TRIAL_ACCOUNT", {
                "simulated": True,
                "to": formatted_number,
                "message": message,
                "original_error": error_message,
                "error_code": error_code,
                "note": "SMS simulated due to Twilio trial account geographic restrictions"
            }
        elif error_code == 21608:
            # Unverified number in trial account - simulate sending
            logger.warning("Recipient number not verified in Twilio trial account.")
            logger.warning("Simulating SMS delivery for trial account.")

            # Return success with simulation details
            logger.info(f"SIMULATED SMS to {formatted_number}: '{message}'")
            return True, "SIMULATED_DUE_TO_UNVERIFIED_NUMBER", {
                "simulated": True,
                "to": formatted_number,
                "message": message,
                "original_error": error_message,
                "error_code": error_code,
                "note": "SMS simulated due to unverified number in Twilio trial account"
            }
        else:
            return False, error_message, {"error_type": "TWILIO_API_ERROR", "error_code": error_code}
    except Exception as e:
        logger.error(f"SMS sending failed: {str(e)}")
        return False, str(e), {"error_type": "UNEXPECTED_ERROR"}


# Program Chair Helper Functions
def is_program_chair(user):
    """Check if the user is a program chair"""
    if not user.is_authenticated:
        return False
    return hasattr(user, 'programchair')

def get_current_school_year():
    """Get the current school year in format YYYY-YYYY"""
    current_year = timezone.now().year
    return f"{current_year}-{current_year + 1}"

def get_current_semester():
    """Get the current semester based on the current month"""
    month = timezone.now().month
    if 1 <= month <= 5:  # January to May
        return "2ND"
    elif 6 <= month <= 10:  # June to October
        return "1ST"
    else:  # November to December
        return "SUM"

def get_semester_display(semester_code):
    """Convert semester code to display text"""
    semester_map = {
        "1ST": "First Semester",
        "2ND": "Second Semester",
        "SUM": "Summer"
    }
    return semester_map.get(semester_code, semester_code)

def get_year_level_display(year_level):
    """Convert year level number to display text"""
    if year_level == 1:
        return "1st Year"
    elif year_level == 2:
        return "2nd Year"
    elif year_level == 3:
        return "3rd Year"
    else:
        return f"{year_level}th Year"
