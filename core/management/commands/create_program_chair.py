from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Staff, Office, Dean, ProgramChair  # Import the models we need


class Command(BaseCommand):
    help = "Create a Program Chair user account."

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help="Email of the Program Chair")
        parser.add_argument('password', type=str, help="Password for the Program Chair")
        parser.add_argument('--dean', type=str, help="Dean name to associate with the Program Chair", required=False)
        parser.add_argument('--designation', type=str, help="Designation for the Program Chair (e.g., SAFES DEAN)", required=False)

    def handle(self, *args, **kwargs):
        email = kwargs['email']
        password = kwargs['password']
        dean_name = kwargs.get('dean')
        designation = kwargs.get('designation')
        username = email.split('@')[0]  # Use part of the email as the username

        # Get the PROGRAM CHAIR office
        try:
            office = Office.objects.get(name="PROGRAM CHAIR")
        except Office.DoesNotExist:
            # If it doesn't exist, use the data migration or management command to create it
            self.stdout.write(self.style.WARNING("PROGRAM CHAIR office not found. Please run migrations or the ensure_required_offices command."))
            return

        # Get dean if specified
        dean = None
        if dean_name:
            try:
                dean = Dean.objects.get(name=dean_name)
                self.stdout.write(self.style.SUCCESS(f"Found dean: {dean.name}"))
            except Dean.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"⚠ Dean '{dean_name}' not found. Creating Program Chair without dean association."))

        # Check if the user already exists
        user, user_created = User.objects.get_or_create(username=username, email=email)
        if user_created:
            user.set_password(password)
            user.is_staff = True  # Allow admin panel access
            user.is_superuser = False
            user.save()

            # Assign user as a Program Chair in Staff table
            Staff.objects.create(user=user, office=office, role="Program Chair")

            # Create Program Chair with dean and designation if provided
            program_chair = ProgramChair.objects.create(
                user=user,
                dean=dean,
                designation=designation
            )

            self.stdout.write(self.style.SUCCESS(f"✅ Program Chair {email} created successfully!"))
            self.stdout.write(self.style.SUCCESS(f"Title: {program_chair.get_title()}"))
        else:
            # Update existing Program Chair if needed
            try:
                program_chair = ProgramChair.objects.get(user=user)
                if dean:
                    program_chair.dean = dean
                if designation:
                    program_chair.designation = designation
                program_chair.save()
                self.stdout.write(self.style.WARNING(f"⚠ Program Chair {email} already exists. Updated dean and designation if provided."))
                self.stdout.write(self.style.SUCCESS(f"Title: {program_chair.get_title()}"))
            except ProgramChair.DoesNotExist:
                # Create Program Chair for existing user
                program_chair = ProgramChair.objects.create(
                    user=user,
                    dean=dean,
                    designation=designation
                )
                self.stdout.write(self.style.WARNING(f"⚠ User {email} already exists. Created Program Chair association."))
                self.stdout.write(self.style.SUCCESS(f"Title: {program_chair.get_title()}"))
