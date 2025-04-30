from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from django.templatetags.static import static

SEMESTER_CHOICES = [
    ('1ST_MID', '1st Sem - Midterm'),
    ('1ST_FIN', '1st Sem - Final'),
    ('2ND_MID', '2nd Sem - Midterm'),
    ('2ND_FIN', '2nd Sem - Final'),
    ('SUM', 'Summer'),
]

class SystemSettings(models.Model):
    """Model to store system-wide settings and configurations"""
    school_year = models.CharField(max_length=9, help_text="Current school year in format YYYY-YYYY")
    semester = models.CharField(max_length=7, choices=SEMESTER_CHOICES, help_text="Current semester")
    clearance_active = models.BooleanField(default=False, help_text="Whether clearance requests are currently active")
    maintenance_mode = models.BooleanField(default=False, help_text="Whether the system is in maintenance mode")
    email_notifications = models.BooleanField(default=True, help_text="Whether email notifications are enabled")
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return f"System Settings - {self.school_year} {self.get_semester_display()}"

    def get_semester_display(self):
        """Get the display name for the semester"""
        for code, name in SEMESTER_CHOICES:
            if code == self.semester:
                return name
        return self.semester

    @classmethod
    def get_settings(cls):
        """Get the current system settings, creating default if none exist"""
        settings = cls.objects.first()
        if not settings:
            # Create default settings
            current_year = timezone.now().year
            school_year = f"{current_year}-{current_year + 1}"

            # Determine current semester based on month
            month = timezone.now().month
            if 1 <= month <= 5:  # January to May
                semester = "2ND_MID" if month <= 3 else "2ND_FIN"
            elif 6 <= month <= 10:  # June to October
                semester = "1ST_MID" if month <= 8 else "1ST_FIN"
            else:  # November to December
                semester = "SUM"

            settings = cls.objects.create(
                school_year=school_year,
                semester=semester,
                clearance_active=False,
                maintenance_mode=False,
                email_notifications=True
            )
        return settings

class Dean(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='dean_logos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    dean = models.ForeignKey(Dean, on_delete=models.PROTECT, related_name='courses')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

class Office(models.Model):
    OFFICE_TYPES = [
        ('SET', 'SET'),
        ('STE', 'STE'),
        ('SOCJE', 'SOCJE'),
        ('SAFES', 'SAFES'),
        ('SSB SET', 'SSB SET'),
        ('SSB STE', 'SSB STE'),
        ('SSB SOCJE', 'SSB SOCJE'),
        ('SSB SAFES', 'SSB SAFES'),
        ('OTHER', 'OTHER'),
    ]
    name = models.CharField(max_length=255, unique=True)
    office_type = models.CharField(max_length=50, choices=OFFICE_TYPES, default='OTHER')
    affiliated_dean = models.ForeignKey(Dean, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='staff')
    role = models.CharField(max_length=100)
    is_dormitory_owner = models.BooleanField(default=False)
    boarding_house_address = models.TextField(verbose_name="Boarding House Address", null=True, blank=True)
    profile_picture = models.ImageField(upload_to='staff_profiles/', null=True, blank=True)

    def get_profile_picture_url(self):
        return self.profile_picture.url if self.profile_picture else static('img/default-profile.png')

    def get_full_name(self):
        return self.user.get_full_name()

    def __str__(self):
        return f"{self.get_full_name()} - {self.office.name}"

class ProgramChair(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dean = models.ForeignKey(Dean, on_delete=models.SET_NULL, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='program_chair_profiles/', null=True, blank=True)
    designation = models.CharField(max_length=100, blank=True, null=True)

    def get_profile_picture_url(self):
        return self.profile_picture.url if self.profile_picture else static('img/default-profile.png')

    def get_full_name(self):
        return self.user.get_full_name()

    def get_title(self):
        """Return the formatted title for the program chair"""
        if self.designation:
            return f"Program Chair {self.designation}"
        elif self.dean:
            return f"Program Chair {self.dean.name}"
        else:
            return "Program Chair"

    def __str__(self):
        return self.get_full_name()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='admin_profiles/', null=True, blank=True)

    def get_profile_picture_url(self):
        return self.profile_picture.url if self.profile_picture else static('img/default-profile.png')

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if instance.is_superuser:
        UserProfile.objects.get_or_create(user=instance)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    program_chair = models.ForeignKey('ProgramChair', on_delete=models.SET_NULL, null=True, blank=True)
    dormitory_owner = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, blank=True, related_name='dormitory_students')
    year_level = models.IntegerField()
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    is_boarder = models.BooleanField(default=False)
    boarder_since = models.DateTimeField(verbose_name="Date Started as a Boarder", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='student_profiles/', null=True, blank=True)

    def get_profile_picture_url(self):
        if self.profile_picture and self.profile_picture.url:
            return self.profile_picture.url
        return static('img/default-profile.png')  # Make sure this file exists in your static folder

    def save(self, *args, **kwargs):
        """Override save method to handle boarder_since field and dormitory owner changes"""
        # If this is an existing student (has an ID)
        if self.pk:
            try:
                old_instance = Student.objects.get(pk=self.pk)

                # If student is becoming a boarder and doesn't have a boarder_since date
                if self.is_boarder and not old_instance.is_boarder and not self.boarder_since:
                    self.boarder_since = timezone.now()

                # If student is no longer assigned to a dormitory owner, set is_boarder to False
                if old_instance.dormitory_owner and not self.dormitory_owner:
                    self.is_boarder = False
                    # We keep the boarder_since date for historical purposes

                # If student is assigned to a new dormitory owner and is marked as a boarder
                if self.dormitory_owner and (not old_instance.dormitory_owner or old_instance.dormitory_owner.id != self.dormitory_owner.id) and self.is_boarder:
                    # Update boarder_since to now if changing dormitory owners
                    self.boarder_since = timezone.now()

            except Student.DoesNotExist:
                pass
        # If this is a new student and is a boarder
        elif self.is_boarder and not self.boarder_since and self.dormitory_owner:
            self.boarder_since = timezone.now()

        super().save(*args, **kwargs)

    def approve_student(self, admin_user):
        """Approve a student's registration."""
        self.is_approved = True
        self.user.is_active = True
        self.rejection_reason = None
        self.user.save()
        self.save()

    def reject_student(self, reason):
        """Reject a student's registration."""
        self.is_approved = False
        self.user.is_active = False
        self.rejection_reason = reason
        self.user.save()
        self.save()

    def get_full_name(self):
        return self.user.get_full_name()

    @property
    def has_complete_clearance(self):
        """Check if student has a complete clearance for the current school year and semester"""
        # Get the current clearance
        clearance = self.get_current_clearance()

        # Check if the clearance exists, is cleared, and program chair has approved it
        return clearance is not None and clearance.is_cleared and clearance.program_chair_approved

    def get_current_clearance(self):
        """Get the current clearance for the student based on the current school year and semester"""
        # Get current school year and semester from system settings
        settings = SystemSettings.get_settings()
        school_year = settings.school_year
        semester = settings.semester

        return self.clearances.filter(
            school_year=school_year,
            semester=semester
        ).first()

    def get_current_permit(self):
        """Check if the student has a permit for the current school year and semester"""
        clearance = self.get_current_clearance()
        if clearance and clearance.is_cleared and clearance.program_chair_approved:
            return clearance
        return None

    def sync_approval_status(self):
        """Sync the is_approved field with user.is_active"""
        if self.is_approved != self.user.is_active:
            self.is_approved = self.user.is_active
            self.save(update_fields=['is_approved'])

    def __str__(self):
        return f"{self.get_full_name()} ({self.student_id})"

class ClearanceRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='clearance_requests')
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='clearance_requests')
    clearance = models.ForeignKey('Clearance', on_delete=models.CASCADE, related_name='requests')
    school_year = models.CharField(max_length=9)
    semester = models.CharField(max_length=7, choices=SEMESTER_CHOICES)
    status_choices = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='pending')
    remarks = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    request_date = models.DateTimeField(auto_now_add=True)
    reviewed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['student', 'office', 'school_year', 'semester']
        ordering = ['-school_year', '-semester', '-request_date']

    def __str__(self):
        return f"{self.student} - {self.office} - {self.school_year} {self.get_semester_display()} ({self.status})"

    def validate_staff_permission(self, staff):
        if staff.office != self.office:
            raise PermissionError(f"No permission to handle requests for {self.office.name}")
        if self.office.name == "DORMITORY":
            if not staff.is_dormitory_owner or self.student.dormitory_owner != staff:
                raise PermissionError("Dormitory clearance permission denied")
        if self.office.name.startswith('SSB') and self.office.affiliated_dean != self.student.course.dean:
            raise PermissionError("SSB clearance permission denied")

    def approve(self, staff):
        self.validate_staff_permission(staff)
        self.status = "approved"
        self.reviewed_by = staff
        self.reviewed_date = timezone.now()
        self.notes = None  # Clear notes on approval
        self.save()
        self.clearance.check_clearance()

    def deny(self, staff, reason):
        if not reason:
            raise ValueError("Reason required for denial")
        self.validate_staff_permission(staff)
        self.status = "denied"
        self.reviewed_by = staff
        self.notes = reason
        self.reviewed_date = timezone.now()
        self.save()
        self.clearance.check_clearance()

    def can_be_handled_by(self, staff):
        try:
            self.validate_staff_permission(staff)
            return True
        except PermissionError:
            return False

class Clearance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='clearances')
    school_year = models.CharField(max_length=9)
    semester = models.CharField(max_length=7, choices=SEMESTER_CHOICES)
    is_cleared = models.BooleanField(default=False)
    cleared_date = models.DateTimeField(null=True, blank=True)
    program_chair_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'school_year', 'semester']
        ordering = ['-school_year', '-semester']

    def check_clearance(self):
        # Check if there are any pending or denied requests
        pending_or_denied = self.requests.filter(status__in=['pending', 'denied']).exists()
        was_cleared = self.is_cleared  # Store previous state

        # If there are no pending or denied requests, mark as cleared
        self.is_cleared = not pending_or_denied

        # Set cleared date if newly cleared
        if self.is_cleared and not was_cleared:
            self.cleared_date = timezone.now()
            # Automatically set program_chair_approved to True when clearance is cleared
            self.program_chair_approved = True
        # If no longer cleared, reset cleared date and program_chair_approved
        elif not self.is_cleared:
            self.cleared_date = None
            self.program_chair_approved = False

        self.save()
        return self.is_cleared  # Return the current clearance status

    def unlock_permit(self):
        # This method is kept for backward compatibility
        # The functionality is now handled in check_clearance
        pass

    @property
    def pending_count(self):
        """Return the count of pending clearance requests"""
        return self.requests.filter(status='pending').count()

    @property
    def approved_count(self):
        """Return the count of approved clearance requests"""
        return self.requests.filter(status='approved').count()

    @property
    def denied_count(self):
        """Return the count of denied clearance requests"""
        return self.requests.filter(status='denied').count()

    @property
    def total_requests(self):
        """Return the total number of clearance requests"""
        return self.requests.count()

    @property
    def progress_percentage(self):
        """Calculate the progress percentage based on approved requests"""
        if self.total_requests == 0:
            return 0
        return int((self.approved_count / self.total_requests) * 100)

    @property
    def status_label(self):
        """Return a human-readable status label"""
        if self.is_cleared:
            return "Cleared"
        elif self.denied_count > 0:
            return "Denied"
        elif self.approved_count > 0:
            return "In Progress"
        else:
            return "Pending"

    def __str__(self):
        status = 'Cleared' if self.is_cleared else 'Not Cleared'
        permit_status = 'Permit Unlocked' if self.program_chair_approved else 'Permit Locked'
        return f"{self.student} - {self.school_year} {self.get_semester_display()} - {status} - {permit_status}"



