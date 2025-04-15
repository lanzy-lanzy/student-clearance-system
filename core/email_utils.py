import logging
import time
import socket
import ssl
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTPException
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string, TemplateDoesNotExist
from django.template import engines

logger = logging.getLogger(__name__)

def send_direct_email(to_email, subject, message, html_message=None):
    """
    Send an email using direct SMTP connection with retry logic.
    This bypasses Django's email backend for more reliable sending.

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
    logger.info(f"Attempting to send direct email to: {to_email}")

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
            logger.info(f"Direct email sending attempt {attempts}/{max_retries} to {to_email}")

            # Create a multipart message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.EMAIL_HOST_USER
            msg['To'] = ", ".join(to_email)

            # Attach plain text and HTML parts
            part1 = MIMEText(message, 'plain')
            msg.attach(part1)

            if html_message:
                part2 = MIMEText(html_message, 'html')
                msg.attach(part2)

            # Connect to the SMTP server
            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.ehlo()
                if settings.EMAIL_USE_TLS:
                    server.starttls()
                    server.ehlo()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.sendmail(settings.EMAIL_HOST_USER, to_email, msg.as_string())

            logger.info(f"Direct email sent successfully to {to_email} on attempt {attempts}")
            return True, "Email sent successfully", {"status": "sent", "attempts": attempts}

        except (socket.error, ssl.SSLError, SMTPException) as e:
            last_exception = e
            error_type = type(e).__name__
            logger.warning(f"Error on attempt {attempts} sending direct email to {to_email}: {error_type} - {str(e)}")

            # Log more detailed information about the error
            if isinstance(e, socket.error):
                logger.warning(f"Socket error details: Error code: {e.errno if hasattr(e, 'errno') else 'N/A'}")
                logger.warning(f"Socket error message: {e.strerror if hasattr(e, 'strerror') else 'N/A'}")
            elif isinstance(e, ssl.SSLError):
                logger.warning(f"SSL error details: {e.reason if hasattr(e, 'reason') else 'N/A'}")
            elif isinstance(e, SMTPException):
                logger.warning(f"SMTP error details: {e.smtp_code if hasattr(e, 'smtp_code') else 'N/A'} - {e.smtp_error if hasattr(e, 'smtp_error') else 'N/A'}")

            # If this is the last attempt, return the error
            if attempts >= max_retries:
                logger.error(f"All {max_retries} attempts to send direct email to {to_email} failed with error: {error_type} - {str(e)}")
                return False, str(e), {"error_type": error_type, "attempts": attempts}

            # Wait before retrying
            time.sleep(retry_delay)
        except Exception as e:
            last_exception = e
            error_type = type(e).__name__
            logger.warning(f"Unexpected error on attempt {attempts} sending direct email to {to_email}: {error_type} - {str(e)}")

            # If this is the last attempt, return the error
            if attempts >= max_retries:
                logger.error(f"All {max_retries} attempts to send direct email to {to_email} failed with unexpected error: {error_type} - {str(e)}")
                return False, str(e), {"error_type": error_type, "attempts": attempts}

            # Wait before retrying
            time.sleep(retry_delay)

def send_email(to_email, subject, message, html_message=None):
    """
    Send an email using Django's email functionality with retry logic.
    If that fails, falls back to direct SMTP connection.

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
                    logger.info(f"Trying direct SMTP connection as fallback...")
                    return send_direct_email(to_email, subject, message, html_message)

                # Wait before retrying
                time.sleep(retry_delay)

        except (socket.error, ssl.SSLError, SMTPException) as e:
            last_exception = e
            error_type = type(e).__name__
            logger.warning(f"Error on attempt {attempts} sending email to {to_email}: {error_type} - {str(e)}")

            # Log more detailed information about the error
            if isinstance(e, socket.error):
                logger.warning(f"Socket error details: Error code: {e.errno if hasattr(e, 'errno') else 'N/A'}")
                logger.warning(f"Socket error message: {e.strerror if hasattr(e, 'strerror') else 'N/A'}")
            elif isinstance(e, ssl.SSLError):
                logger.warning(f"SSL error details: {e.reason if hasattr(e, 'reason') else 'N/A'}")
            elif isinstance(e, SMTPException):
                logger.warning(f"SMTP error details: {e.smtp_code if hasattr(e, 'smtp_code') else 'N/A'} - {e.smtp_error if hasattr(e, 'smtp_error') else 'N/A'}")

            # If this is the last attempt, try direct SMTP as fallback
            if attempts >= max_retries:
                logger.error(f"All {max_retries} attempts to send email to {to_email} failed with error: {error_type} - {str(e)}")
                logger.info(f"Trying direct SMTP connection as fallback...")
                return send_direct_email(to_email, subject, message, html_message)

            # Wait before retrying
            time.sleep(retry_delay)
        except Exception as e:
            last_exception = e
            error_type = type(e).__name__
            logger.warning(f"Unexpected error on attempt {attempts} sending email to {to_email}: {error_type} - {str(e)}")

            # If this is the last attempt, try direct SMTP as fallback
            if attempts >= max_retries:
                logger.error(f"All {max_retries} attempts to send email to {to_email} failed with unexpected error: {error_type} - {str(e)}")
                logger.info(f"Trying direct SMTP connection as fallback...")
                return send_direct_email(to_email, subject, message, html_message)

            # Wait before retrying
            time.sleep(retry_delay)

def template_exists(template_name):
    """
    Check if a template exists in any of the template directories.

    Args:
        template_name (str): The name of the template to check

    Returns:
        bool: True if the template exists, False otherwise
    """
    try:
        # Try to find the template
        template = engines['django'].get_template(template_name)
        return True
    except TemplateDoesNotExist:
        return False

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
        # Use absolute URL for login with domain
        'login_url': f"http://127.0.0.1:8000{settings.LOGIN_URL if hasattr(settings, 'LOGIN_URL') and settings.LOGIN_URL.startswith('/') else '/' + settings.LOGIN_URL if hasattr(settings, 'LOGIN_URL') else '/login/'}"
    }

    # Plain text message as fallback
    plain_message = f"""
Hello {student_name},

Your registration for {student.course.code} has been approved. You can now log in to the system.

{f"Note: {notes}" if notes else ""}

Thank you,
Student Clearance System
"""

    # Check if HTML template exists before rendering
    html_message = None
    template_name = 'emails/student_approval.html'

    if template_exists(template_name):
        try:
            html_message = render_to_string(template_name, context)
            logger.info(f"HTML template '{template_name}' rendered successfully")
        except Exception as e:
            logger.error(f"Error rendering HTML template '{template_name}': {str(e)}")
    else:
        logger.warning(f"HTML template '{template_name}' not found, using plain text only")

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
        'support_email': settings.DEFAULT_FROM_EMAIL,
        # Use absolute URL for login with domain (in case we need it in the rejection template)
        'login_url': f"http://127.0.0.1:8000{settings.LOGIN_URL if hasattr(settings, 'LOGIN_URL') and settings.LOGIN_URL.startswith('/') else '/' + settings.LOGIN_URL if hasattr(settings, 'LOGIN_URL') else '/login/'}"
    }

    # Plain text message as fallback
    plain_message = f"""
Hello {student_name},

Your registration for {student.course.code} has been rejected.

Reason: {reason}

If you have any questions, please contact our support team at {settings.DEFAULT_FROM_EMAIL}.

Thank you,
Student Clearance System
"""

    # Check if HTML template exists before rendering
    html_message = None
    template_name = 'emails/student_rejection.html'

    if template_exists(template_name):
        try:
            html_message = render_to_string(template_name, context)
            logger.info(f"HTML template '{template_name}' rendered successfully")
        except Exception as e:
            logger.error(f"Error rendering HTML template '{template_name}': {str(e)}")
    else:
        logger.warning(f"HTML template '{template_name}' not found, using plain text only")

    return send_email(student.user.email, subject, plain_message, html_message)
