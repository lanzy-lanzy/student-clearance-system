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

def test_sms_functionality():
    """Test the SMS functionality with different scenarios."""

    # Test options
    options = [
        "1. Send SMS to Philippines number (+639510440202) - Will simulate due to trial account",
        "2. Send SMS to any other number in test mode - Will simulate sending",
        "3. Exit"
    ]

    while True:
        print("\n=== SMS Testing Options ===")
        for option in options:
            print(option)

        choice = input("\nEnter your choice (1-3): ")

        if choice == "1":
            # Send to Philippines number
            ph_number = "+639510440202"
            message = input("Enter your message: ")

            if not message:
                message = "This is a test message from the Student Clearance System."

            logging.info(f"Sending SMS to Philippines number {ph_number}")
            logging.info("Note: With a trial account, this will be simulated due to geographic restrictions.")

            success, result, details = send_sms(ph_number, message, test_mode=False)

            if success:
                logging.info(f"SMS processed successfully! ID: {result}")
                logging.info(f"Response details: {details}")

                # Display the message details
                print("\n=== SMS Result ===")
                print(f"To: {ph_number}")
                print(f"Message: {message}")

                if details.get('simulated'):
                    print(f"Status: Simulated ({details.get('note')})")
                    print("Note: In production with a paid account, this would send a real SMS.")
                else:
                    print("Status: Sent")
            else:
                logging.error(f"SMS failed: {result}")
                logging.error(f"Error details: {details}")

        elif choice == "2":
            # Send to any number in test mode
            number = input("Enter a phone number (e.g., +639123456789): ")
            message = input("Enter your message: ")

            if not message:
                message = "This is a test message from the Student Clearance System."

            logging.info(f"Simulating SMS to {number} in test mode")

            success, result, details = send_sms(number, message, test_mode=True)

            if success:
                logging.info(f"SMS simulation successful! ID: {result}")
                logging.info(f"Response details: {details}")

                # Display the message details
                print("\n=== SMS Simulation Result ===")
                print(f"To: {number}")
                print(f"Message: {message}")
                print(f"Status: Simulated (test mode)")
            else:
                logging.error(f"SMS simulation failed: {result}")
                logging.error(f"Error details: {details}")

        elif choice == "3":
            logging.info("Exiting SMS testing")
            break

        else:
            logging.warning("Invalid choice. Please enter 1, 2, or 3.")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    test_sms_functionality()
