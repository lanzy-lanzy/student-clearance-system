from core.utils import send_sms

# Test the send_sms function
success, result, details = send_sms('+639510440202', 'Test message', test_mode=True)
print(f"Success: {success}")
print(f"Result: {result}")
print(f"Details: {details}")
