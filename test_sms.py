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

from core.utils import send_sms, validate_phone_number, format_phone_number

def test_phone_number_formatting():
    """Test the phone number formatting function with various inputs."""
    test_cases = [
        ('09510440202', '+639510440202'),  # Philippines number starting with 09
        ('639510440202', '+639510440202'),  # Philippines number starting with 639
        ('+639510440202', '+639510440202'),  # Already formatted Philippines number
        ('0951-044-0202', '+639510440202'),  # With dashes
        ('0951 044 0202', '+639510440202'),  # With spaces
        ('(0951) 044-0202', '+639510440202'),  # With parentheses
        ('123456789', None),  # Invalid number (too short)
        ('', None),  # Empty string
        (None, None),  # None value
    ]

    print("\n=== Testing Phone Number Formatting ===")
    for input_number, expected_output in test_cases:
        result = format_phone_number(input_number)
        status = "✓" if result == expected_output else "✗"
        print(f"{status} Input: '{input_number}' → Output: '{result}' (Expected: '{expected_output}')")

def test_phone_number_validation():
    """Test the phone number validation function with various inputs."""
    test_cases = [
        ('+639510440202', True),  # Valid Philippines number
        ('+639123456789', True),  # Valid Philippines number
        ('+6391234567', False),   # Too short
        ('+63912345678901', False),  # Too long
        ('+123456789012', False),  # Not Philippines
        ('09510440202', False),   # Missing + prefix
        ('', False),              # Empty string
        (None, False),            # None value
    ]

    print("\n=== Testing Phone Number Validation ===")
    for input_number, expected_output in test_cases:
        result = validate_phone_number(input_number)
        status = "✓" if result == expected_output else "✗"
        print(f"{status} Input: '{input_number}' → Valid: {result} (Expected: {expected_output})")

def test_sms_sending():
    """Test sending an SMS to a verified number."""
    verified_number = '+639510440202'

    # Get custom message from user
    print("\n=== Send SMS to Philippines Number ===")
    print(f"This will send a real SMS to your verified number: {verified_number}")
    message = input("Enter your custom message (or press Enter for default message): ")

    if not message:
        message = "This is a test message from the Student Clearance System."

    # Format the number first
    formatted_number = format_phone_number(verified_number)
    print(f"Formatted number: {formatted_number}")

    # Validate the number
    is_valid = validate_phone_number(formatted_number)
    print(f"Number validation: {'Valid' if is_valid else 'Invalid'}")

    # Send the SMS
    print(f"Sending message: '{message}'")
    success, result, details = send_sms(formatted_number, message, test_mode=False)

    if success:
        print("✓ SMS sent successfully!")
        if details.get('simulated'):
            print(f"Note: {details.get('note')}")
    else:
        print("✗ Failed to send SMS. Check the logs for details.")
        print(f"Error: {result}")

if __name__ == "__main__":
    # Test the phone number formatting function
    test_phone_number_formatting()

    # Test the phone number validation function
    test_phone_number_validation()

    # Ask if the user wants to send a real SMS
    send_real_sms = input("\nDo you want to send a real SMS to test the functionality? (y/n): ")
    if send_real_sms.lower() == 'y':
        test_sms_sending()
    else:
        print("SMS sending test skipped.")
