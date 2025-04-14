from core.utils import send_sms

# Test the send_sms function with a real SMS
success, result, details = send_sms('+639510440202', 'Test message', test_mode=False)
print(f"Success: {success}")
print(f"Result: {result}")
print(f"Details: {details}")
