from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from django.templatetags.static import static

SEMESTER_CHOICES = [
    ('1ST', 'First Semester'),
    ('2ND', 'Second Semester'),
    ('SUM', 'Summer'),
]

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
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='student_profiles/', null=True, blank=True)

    def get_profile_picture_url(self):
        if self.profile_picture and self.profile_picture.url:
            return self.profile_picture.url
        return static('img/default-profile.png')  # Make sure this file exists in your static folder

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
        current_year = timezone.now().year
        school_year = f"{current_year}-{current_year + 1}"

        # Determine current semester based on month
        month = timezone.now().month
        if 1 <= month <= 5:  # January to May
            semester = "2ND"
        elif 6 <= month <= 10:  # June to October
            semester = "1ST"
        else:  # November to December
            semester = "SUM"

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
    semester = models.CharField(max_length=3, choices=SEMESTER_CHOICES)
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
    semester = models.CharField(max_length=3, choices=SEMESTER_CHOICES)
    is_cleared = models.BooleanField(default=False)
    cleared_date = models.DateTimeField(null=True, blank=True)
    program_chair_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'school_year', 'semester']
        ordering = ['-school_year', '-semester']

    def check_clearance(self):
        pending_or_denied = self.requests.filter(status__in=['pending', 'denied']).exists()
        was_cleared = self.is_cleared  # Store previous state
        self.is_cleared = not pending_or_denied

        # Set cleared date if newly cleared
        if self.is_cleared and not was_cleared:
            self.cleared_date = timezone.now()
            # Automatically set program_chair_approved to True when clearance is cleared
            self.program_chair_approved = True
        # If no longer cleared, reset cleared date
        elif not self.is_cleared:
            self.cleared_date = None

        self.save()

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



