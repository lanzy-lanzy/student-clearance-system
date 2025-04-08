import logging
import http.client
import json

# Keep Twilio imports for backward compatibility
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logging.warning("Twilio library not available. SMS will be sent using Infobip only.")

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor

# Twilio credentials - should be loaded from environment variables in production
TWILIO_ACCOUNT_SID = 'YOUR_TWILIO_ACCOUNT_SID'  # Replace with actual SID in production
TWILIO_AUTH_TOKEN = 'YOUR_TWILIO_AUTH_TOKEN'  # Replace with actual token in production
TWILIO_PHONE_NUMBER = 'YOUR_TWILIO_PHONE_NUMBER'  # Replace with actual phone number in production

# Infobip credentials - should be loaded from environment variables in production
INFOBIP_API_HOST = 'YOUR_INFOBIP_API_HOST'  # Replace with actual host in production
INFOBIP_API_KEY = 'YOUR_INFOBIP_API_KEY'  # Replace with actual API key in production
INFOBIP_SENDER = 'YOUR_INFOBIP_SENDER'  # Replace with actual sender in production

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


def send_sms(to_number, message, test_mode=False):
    """
    Send an SMS message using the preferred provider (Infobip).
    This function maintains backward compatibility with the old Twilio implementation.

    Args:
        to_number (str): The recipient's phone number in E.164 format (e.g., +639123456789)
        message (str): The message content to send
        test_mode (bool): If True, will simulate sending without actually calling the SMS API

    Returns:
        bool: True if the message was sent successfully, False otherwise
        str: Message ID if successful, error message if failed
        dict: Additional information about the message status
    """
    # Debug information
    logging.info(f"Attempting to send SMS - To: {to_number}, Test Mode: {test_mode}")

    # Use Infobip as the primary SMS provider
    return send_sms_infobip(to_number, message, test_mode)
