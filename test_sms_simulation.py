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

def test_sms_simulation():
    """Test the SMS simulation for verified number."""
    
    # Test options
    options = [
        "1. Simulate sending SMS to verified number (+639510440202)",
        "2. Simulate sending SMS to any other number",
        "3. Exit"
    ]
    
    while True:
        print("\n=== SMS Testing Options ===")
        for option in options:
            print(option)
            
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            # Simulate sending to verified number
            verified_number = "+639510440202"
            message = input("Enter your message: ")
            
            if not message:
                message = "This is a test message from the Student Clearance System."
                
            logging.info(f"Simulating SMS to verified number {verified_number}")
            
            success, result, details = send_sms(verified_number, message, test_mode=False)
            
            if success:
                logging.info(f"SMS simulation successful! ID: {result}")
                logging.info(f"Response details: {details}")
                
                # Display the message that would be sent
                print("\n=== SMS Simulation Result ===")
                print(f"To: {verified_number}")
                print(f"Message: {message}")
                print(f"Status: Simulated (would be sent in production)")
            else:
                logging.error(f"SMS simulation failed: {result}")
                logging.error(f"Error details: {details}")
                
        elif choice == "2":
            # Simulate sending to any number
            number = input("Enter a phone number (e.g., +639123456789): ")
            message = input("Enter your message: ")
            
            if not message:
                message = "This is a test message from the Student Clearance System."
                
            logging.info(f"Simulating SMS to {number}")
            
            success, result, details = send_sms(number, message, test_mode=True)
            
            if success:
                logging.info(f"SMS simulation successful! ID: {result}")
                logging.info(f"Response details: {details}")
                
                # Display the message that would be sent
                print("\n=== SMS Simulation Result ===")
                print(f"To: {number}")
                print(f"Message: {message}")
                print(f"Status: Simulated (would be sent in production)")
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
    test_sms_simulation()
