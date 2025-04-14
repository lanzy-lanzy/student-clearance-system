import logging
import time
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

def send_email(to_email, subject, message, html_message=None):
    """
    Send an email using Django's email functionality with retry logic.

    Args:
        to_email (str or list): The recipient's email address or a list of email addresses
        subject (str): The email subject
        message (str): The plain text message content
        html_message (str, optional): The HTML message content. Defaults to None.

    Returns:
        bool: True if the email was sent successfully, False otherwise
        str: Error message if failed
        dict: Additional information about the email status
    """
    logger.info(f"Attempting to send email to: {to_email}")

    if not to_email:
        logger.error("Email sending failed: No email address provided")
        return False, "No email address provided", {"error_code": "NO_EMAIL"}

    # Convert single email to list format
    if isinstance(to_email, str):
        to_email = [to_email]

    # Get retry settings from Django settings or use defaults
    max_retries = getattr(settings, 'EMAIL_MAX_RETRIES', 3)
    retry_delay = getattr(settings, 'EMAIL_RETRY_DELAY', 5)

    # Initialize variables for retry logic
    attempts = 0
    last_exception = None

    # Try sending the email with retries
    while attempts < max_retries:
        attempts += 1
        try:
            logger.info(f"Email sending attempt {attempts}/{max_retries} to {to_email}")

            # Send the email
            sent = send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=to_email,
                html_message=html_message,
                fail_silently=False
            )

            if sent:
                logger.info(f"Email sent successfully to {to_email} on attempt {attempts}")
                return True, "Email sent successfully", {"status": "sent", "attempts": attempts}
            else:
                logger.warning(f"Failed to send email to {to_email} on attempt {attempts}")
                # If this is the last attempt, return failure
                if attempts >= max_retries:
                    logger.error(f"All {max_retries} attempts to send email to {to_email} failed")
                    return False, "Email sending failed after multiple attempts", {"error_code": "SEND_FAILED", "attempts": attempts}

                # Wait before retrying
                time.sleep(retry_delay)

        except Exception as e:
            last_exception = e
            logger.warning(f"Error on attempt {attempts} sending email to {to_email}: {str(e)}")

            # If this is the last attempt, return the error
            if attempts >= max_retries:
                logger.error(f"All {max_retries} attempts to send email to {to_email} failed with error: {str(e)}")
                return False, str(e), {"error_type": "UNEXPECTED_ERROR", "attempts": attempts}

            # Wait before retrying
            time.sleep(retry_delay)

def send_approval_email(student, notes=None):
    """
    Send an approval notification email to a student.

    Args:
        student: The Student model instance
        notes (str, optional): Additional notes to include in the email

    Returns:
        bool: True if the email was sent successfully, False otherwise
        str: Error message if failed
        dict: Additional information about the email status
    """
    if not student.user.email:
        logger.warning(f"Cannot send approval email to student {student.student_id}: No email address available")
        return False, "No email address available", {"error_code": "NO_EMAIL"}

    student_name = student.user.get_full_name()
    subject = f"Your Registration for {student.course.code} Has Been Approved"

    # Create context for email template
    context = {
        'student_name': student_name,
        'course_code': student.course.code,
        'notes': notes,
        'login_url': settings.LOGIN_URL if hasattr(settings, 'LOGIN_URL') else '/login/'
    }

    # Render email templates
    html_message = render_to_string('emails/student_approval.html', context)
    plain_message = f"""
Hello {student_name},

Your registration for {student.course.code} has been approved. You can now log in to the system.

{f"Note: {notes}" if notes else ""}

Thank you,
Student Clearance System
"""

    return send_email(student.user.email, subject, plain_message, html_message)

def send_rejection_email(student, reason):
    """
    Send a rejection notification email to a student.

    Args:
        student: The Student model instance
        reason (str): The reason for rejection

    Returns:
        bool: True if the email was sent successfully, False otherwise
        str: Error message if failed
        dict: Additional information about the email status
    """
    if not student.user.email:
        logger.warning(f"Cannot send rejection email to student {student.student_id}: No email address available")
        return False, "No email address available", {"error_code": "NO_EMAIL"}

    if not reason:
        logger.warning(f"Cannot send rejection email to student {student.student_id}: No reason provided")
        return False, "No rejection reason provided", {"error_code": "NO_REASON"}

    student_name = student.user.get_full_name()
    subject = f"Your Registration for {student.course.code} Has Been Rejected"

    # Create context for email template
    context = {
        'student_name': student_name,
        'course_code': student.course.code,
        'reason': reason,
        'support_email': settings.DEFAULT_FROM_EMAIL
    }

    # Render email templates
    html_message = render_to_string('emails/student_rejection.html', context)
    plain_message = f"""
Hello {student_name},

Your registration for {student.course.code} has been rejected.

Reason: {reason}

If you have any questions, please contact our support team.

Thank you,
Student Clearance System
"""

    return send_email(student.user.email, subject, plain_message, html_message)
