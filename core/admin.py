from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, path
from django.utils import timezone
from django.utils.html import format_html

from core.models import (
    Dean, Course, Office, Staff, Student, ProgramChair,
    UserProfile, ClearanceRequest, Clearance, SEMESTER_CHOICES
)

# Inline admin classes for related models
class CourseInline(admin.TabularInline):
    model = Course
    extra = 1
    fields = ('code', 'name', 'is_active')

class StaffInline(admin.TabularInline):
    model = Staff
    extra = 0
    fields = ('user', 'role', 'is_dormitory_owner')
    raw_id_fields = ('user',)

class ClearanceRequestInline(admin.TabularInline):
    model = ClearanceRequest
    extra = 0
    fields = ('office', 'status', 'reviewed_by', 'request_date')
    readonly_fields = ('request_date',)
    can_delete = False
    max_num = 10
    raw_id_fields = ('reviewed_by',)

class ClearanceInline(admin.TabularInline):
    model = Clearance
    extra = 0
    fields = ('school_year', 'semester', 'is_cleared', 'program_chair_approved', 'cleared_date')
    readonly_fields = ('cleared_date',)
    can_delete = False
    max_num = 5

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'

# Extend User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

# Unregister the original User admin
admin.site.unregister(User)
# Register User with our custom admin
admin.site.register(User, UserAdmin)

@admin.register(Dean)
class DeanAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'course_count', 'student_count', 'logo_preview')
    search_fields = ('name', 'description')
    ordering = ('name',)
    inlines = [CourseInline]
    actions = ['safe_delete_selected', 'reassign_courses']
    readonly_fields = ('related_students', 'related_courses')

    def get_actions(self, request):
        """Override to remove the default delete action"""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def changelist_view(self, request, extra_context=None):
        """Add a warning message to the changelist view"""
        extra_context = extra_context or {}
        extra_context['message'] = (
            "Warning: Deans cannot be deleted directly if they have associated courses. "
            "Use the 'Reassign courses to another dean' action first, then use 'Safely delete selected deans'."
        )
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'reassign/<int:dean_id>/',
                self.admin_site.admin_view(self.reassign_courses_view),
                name='dean_reassign_courses',
            ),
        ]
        return custom_urls + urls

    def delete_view(self, request, object_id, extra_context=None):
        """Override to provide context for the delete confirmation template"""
        obj = self.get_object(request, object_id)
        if obj:
            courses = obj.courses.all()
            extra_context = extra_context or {}
            extra_context['courses'] = courses
        return super().delete_view(request, object_id, extra_context)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # Only show related info when editing an existing object
            fieldsets = list(fieldsets)
            fieldsets.append(
                ('Related Courses', {'fields': ('related_courses',), 'classes': ('collapse',)})
            )
            fieldsets.append(
                ('Related Students', {'fields': ('related_students',), 'classes': ('collapse',)})
            )
        return fieldsets

    def course_count(self, obj):
        return obj.courses.count()
    course_count.short_description = 'Number of Courses'

    def student_count(self, obj):
        # Count students associated with this dean through courses
        return Student.objects.filter(course__dean=obj).count()
    student_count.short_description = 'Number of Students'

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" />', obj.logo.url)
        return "-"
    logo_preview.short_description = 'Logo'

    def related_courses(self, obj):
        """Display a list of courses associated with this dean"""
        courses = obj.courses.all()
        if not courses.exists():
            return "No courses are associated with this dean."

        result = ["<table>",
                 "<tr><th>Code</th><th>Name</th><th>Active</th><th>Students</th></tr>"]

        for course in courses:
            student_count = Student.objects.filter(course=course).count()
            result.append(f"<tr><td>{course.code}</td><td>{course.name}</td>" +
                         f"<td>{'Yes' if course.is_active else 'No'}</td><td>{student_count}</td></tr>")

        result.append("</table>")
        return format_html(''.join(result))
    related_courses.short_description = 'Related Courses'

    def related_students(self, obj):
        """Display a list of students associated with this dean's courses"""
        students = Student.objects.filter(course__dean=obj).select_related('user', 'course')
        if not students.exists():
            return "No students are associated with this dean's courses."

        result = ["<table>",
                 "<tr><th>Student ID</th><th>Name</th><th>Course</th><th>Year Level</th></tr>"]

        for student in students:
            result.append(f"<tr><td>{student.student_id}</td><td>{student.get_full_name()}</td>" +
                         f"<td>{student.course.code}</td><td>{student.year_level}</td></tr>")

        result.append("</table>")
        return format_html(''.join(result))
    related_students.short_description = 'Related Students'

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of deans with associated courses"""
        if obj is None:
            return True
        # Check if there are any courses associated with this dean
        return not obj.courses.exists()

    def delete_model(self, request, obj):
        """Override to prevent direct deletion of deans with associated courses"""
        if obj.courses.exists():
            self.message_user(
                request,
                f"Cannot delete dean '{obj.name}' because it has associated courses. "
                f"Use the 'Reassign courses to another dean' action first.",
                level='error'
            )
            return
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """Override to prevent direct deletion of deans with associated courses"""
        # This is a fallback in case the delete_selected action is somehow triggered
        safe_to_delete = []
        for dean in queryset:
            if not dean.courses.exists():
                safe_to_delete.append(dean.id)

        if safe_to_delete:
            Dean.objects.filter(id__in=safe_to_delete).delete()
            self.message_user(request, f"Successfully deleted {len(safe_to_delete)} dean(s).")

        if len(safe_to_delete) < queryset.count():
            self.message_user(
                request,
                f"Some deans could not be deleted because they have associated courses. "
                f"Use the 'Reassign courses to another dean' action first.",
                level='error'
            )

    def reassign_courses(self, request, queryset):
        """Action to reassign courses from one dean to another"""
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one dean to reassign courses from.", level='error')
            return

        dean = queryset.first()
        return HttpResponseRedirect(f"../reassign/{dean.id}/")
    reassign_courses.short_description = "Reassign courses to another dean"

    def reassign_courses_view(self, request, dean_id):
        """View to reassign courses from one dean to another"""
        from django.db import transaction

        source_dean = self.get_object(request, dean_id)
        if source_dean is None:
            self.message_user(request, "Dean not found.", level='error')
            return redirect('..')

        courses = source_dean.courses.all()
        if not courses.exists():
            self.message_user(request, f"No courses found for dean '{source_dean.name}'.", level='warning')
            return redirect('..')

        # Add student count to each course for display
        for course in courses:
            course.student_count = Student.objects.filter(course=course).count()

        # Get all other deans
        available_deans = Dean.objects.exclude(id=dean_id)

        if request.method == 'POST':
            target_dean_id = request.POST.get('target_dean')
            if not target_dean_id:
                self.message_user(request, "Please select a target dean.", level='error')
                return redirect(request.path)

            try:
                target_dean = Dean.objects.get(id=target_dean_id)

                with transaction.atomic():
                    count = courses.update(dean=target_dean)

                self.message_user(
                    request,
                    f"Successfully reassigned {count} courses from '{source_dean.name}' to '{target_dean.name}'."
                )
                return redirect('..')
            except Exception as e:
                self.message_user(request, f"Error reassigning courses: {e}", level='error')
                return redirect(request.path)

        # Prepare the context for the template
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'source_dean': source_dean,
            'available_deans': available_deans,
            'courses': courses,
            'title': f"Reassign Courses from {source_dean.name}",
        }

        return render(request, 'admin/reassign_courses.html', context)

    def safe_delete_selected(self, request, queryset):
        """Custom action to safely delete deans, checking for protected relationships"""
        safe_to_delete = []
        protected_deans = []

        for dean in queryset:
            # Check if there are any courses associated with this dean
            if dean.courses.exists():
                protected_deans.append(dean)
            else:
                safe_to_delete.append(dean.id)

        # Delete the deans that are safe to delete
        deleted_count = 0
        if safe_to_delete:
            deleted_count = Dean.objects.filter(id__in=safe_to_delete).delete()[0]

        # Provide feedback to the user
        if deleted_count:
            self.message_user(request, f"Successfully deleted {deleted_count} dean(s).")

        if protected_deans:
            dean_names = ", ".join([dean.name for dean in protected_deans])
            self.message_user(
                request,
                f"Could not delete the following dean(s) because they have associated courses: {dean_names}. "
                f"Use the 'Reassign courses to another dean' action before attempting to delete.",
                level='error'
            )
    safe_delete_selected.short_description = "Safely delete selected deans"



@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'dean', 'is_active', 'student_count', 'created_at', 'updated_at')
    list_filter = ('dean', 'is_active')
    search_fields = ('code', 'name')
    ordering = ('code',)
    actions = ['activate_courses', 'deactivate_courses', 'safe_delete_selected', 'reassign_students']
    readonly_fields = ('related_students',)

    def get_actions(self, request):
        """Override to remove the default delete action"""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def changelist_view(self, request, extra_context=None):
        """Add a warning message to the changelist view"""
        extra_context = extra_context or {}
        extra_context['message'] = (
            "Warning: Courses cannot be deleted directly if they have enrolled students. "
            "Use the 'Reassign students to another course' action first, then use 'Safely delete selected courses'."
        )
        return super().changelist_view(request, extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'reassign/<int:course_id>/',
                self.admin_site.admin_view(self.reassign_students_view),
                name='course_reassign_students',
            ),
        ]
        return custom_urls + urls

    def delete_view(self, request, object_id, extra_context=None):
        """Override to provide context for the delete confirmation template"""
        obj = self.get_object(request, object_id)
        if obj:
            students = Student.objects.filter(course=obj).select_related('user')
            extra_context = extra_context or {}
            extra_context['students'] = students
        return super().delete_view(request, object_id, extra_context)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # Only show related students when editing an existing object
            fieldsets = list(fieldsets)
            fieldsets.append(
                ('Related Students', {'fields': ('related_students',), 'classes': ('collapse',)})
            )
        return fieldsets

    def student_count(self, obj):
        return Student.objects.filter(course=obj).count()
    student_count.short_description = 'Number of Students'

    def related_students(self, obj):
        """Display a list of students enrolled in this course"""
        students = Student.objects.filter(course=obj).select_related('user')
        if not students.exists():
            return "No students are enrolled in this course."

        result = ["<table>",
                 "<tr><th>Student ID</th><th>Name</th><th>Year Level</th><th>Contact Number</th></tr>"]

        for student in students:
            result.append(f"<tr><td>{student.student_id}</td><td>{student.get_full_name()}</td>" +
                         f"<td>{student.year_level}</td><td>{student.contact_number or '-'}</td></tr>")

        result.append("</table>")
        return format_html(''.join(result))
    related_students.short_description = 'Enrolled Students'

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of courses with enrolled students"""
        if obj is None:
            return True
        # Check if there are any students associated with this course
        return not Student.objects.filter(course=obj).exists()

    def delete_model(self, request, obj):
        """Override to prevent direct deletion of courses with enrolled students"""
        if Student.objects.filter(course=obj).exists():
            self.message_user(
                request,
                f"Cannot delete course '{obj.code}' because it has enrolled students. "
                f"Use the 'Reassign students to another course' action first.",
                level='error'
            )
            return
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """Override to prevent direct deletion of courses with enrolled students"""
        # This is a fallback in case the delete_selected action is somehow triggered
        safe_to_delete = []
        for course in queryset:
            if not Student.objects.filter(course=course).exists():
                safe_to_delete.append(course.id)

        if safe_to_delete:
            Course.objects.filter(id__in=safe_to_delete).delete()
            self.message_user(request, f"Successfully deleted {len(safe_to_delete)} course(s).")

        if len(safe_to_delete) < queryset.count():
            self.message_user(
                request,
                f"Some courses could not be deleted because they have enrolled students. "
                f"Use the 'Reassign students to another course' action first.",
                level='error'
            )

    def activate_courses(self, request, queryset):
        queryset.update(is_active=True)
    activate_courses.short_description = "Mark selected courses as active"

    def deactivate_courses(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_courses.short_description = "Mark selected courses as inactive"

    def reassign_students(self, request, queryset):
        """Action to reassign students from one course to another"""
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one course to reassign students from.", level='error')
            return

        course = queryset.first()
        return HttpResponseRedirect(f"../reassign/{course.id}/")
    reassign_students.short_description = "Reassign students to another course"

    def reassign_students_view(self, request, course_id):
        """View to reassign students from one course to another"""
        from django.db import transaction

        source_course = self.get_object(request, course_id)
        if source_course is None:
            self.message_user(request, "Course not found.", level='error')
            return redirect('..')

        students = Student.objects.filter(course=source_course).select_related('user')
        if not students.exists():
            self.message_user(request, f"No students found in course '{source_course.code}'.", level='warning')
            return redirect('..')

        # Get all other active courses
        available_courses = Course.objects.filter(is_active=True).exclude(id=course_id)

        if request.method == 'POST':
            target_course_id = request.POST.get('target_course')
            if not target_course_id:
                self.message_user(request, "Please select a target course.", level='error')
                return redirect(request.path)

            try:
                target_course = Course.objects.get(id=target_course_id)

                with transaction.atomic():
                    count = students.update(course=target_course)

                self.message_user(
                    request,
                    f"Successfully reassigned {count} students from '{source_course.code}' to '{target_course.code}'."
                )
                return redirect('..')
            except Exception as e:
                self.message_user(request, f"Error reassigning students: {e}", level='error')
                return redirect(request.path)

        # Prepare the context for the template
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'source_course': source_course,
            'available_courses': available_courses,
            'students': students,
            'title': f"Reassign Students from {source_course.code}",
        }

        return render(request, 'admin/reassign_students.html', context)

    def safe_delete_selected(self, request, queryset):
        """Custom action to safely delete courses, checking for protected relationships"""
        safe_to_delete = []
        protected_courses = []

        for course in queryset:
            # Check if there are any students associated with this course
            if Student.objects.filter(course=course).exists():
                protected_courses.append(course)
            else:
                safe_to_delete.append(course.id)

        # Delete the courses that are safe to delete
        deleted_count = 0
        if safe_to_delete:
            deleted_count = Course.objects.filter(id__in=safe_to_delete).delete()[0]

        # Provide feedback to the user
        if deleted_count:
            self.message_user(request, f"Successfully deleted {deleted_count} course(s).")

        if protected_courses:
            course_names = ", ".join([f"{course.code} - {course.name}" for course in protected_courses])
            self.message_user(
                request,
                f"Could not delete the following course(s) because they have enrolled students: {course_names}. "
                f"Use the 'Reassign students to another course' action before attempting to delete.",
                level='error'
            )
    safe_delete_selected.short_description = "Safely delete selected courses"

@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('name', 'office_type', 'affiliated_dean', 'location', 'contact_number', 'email', 'staff_count', 'created_at')
    list_filter = ('office_type', 'affiliated_dean')
    search_fields = ('name', 'description', 'location', 'contact_number', 'email')
    ordering = ('name',)
    inlines = [StaffInline]

    def staff_count(self, obj):
        return obj.staff.count()
    staff_count.short_description = 'Number of Staff'

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'user_email', 'office', 'role', 'is_dormitory_owner', 'profile_picture_preview')
    list_filter = ('office', 'role', 'is_dormitory_owner')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'role')
    raw_id_fields = ('user', 'office')

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" />', obj.profile_picture.url)
        return "-"
    profile_picture_preview.short_description = 'Profile Picture'

@admin.register(ProgramChair)
class ProgramChairAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'user_email', 'dean', 'designation', 'profile_picture_preview')
    list_filter = ('dean',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'designation')
    raw_id_fields = ('user', 'dean')

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" />', obj.profile_picture.url)
        return "-"
    profile_picture_preview.short_description = 'Profile Picture'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'get_full_name', 'user_email', 'course', 'year_level',
                   'contact_number', 'is_boarder', 'is_approved', 'clearance_status', 'profile_picture_preview')
    list_filter = ('course', 'year_level', 'is_boarder', 'is_approved', 'created_at')
    search_fields = ('student_id', 'user__username', 'user__first_name', 'user__last_name',
                    'user__email', 'contact_number')
    raw_id_fields = ('user', 'course', 'program_chair', 'dormitory_owner')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    inlines = [ClearanceInline]
    actions = ['approve_students', 'reject_students', 'export_students_data']

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def clearance_status(self, obj):
        current_year = timezone.now().year
        school_year = f"{current_year}-{current_year + 1}"
        semester = "1ST"  # Default to first semester

        clearance = obj.clearances.filter(school_year=school_year, semester=semester).first()

        if not clearance:
            return format_html('<span style="color: gray;">No Clearance</span>')
        elif clearance.is_cleared:
            return format_html('<span style="color: green;">Cleared</span>')
        elif clearance.denied_count > 0:
            return format_html('<span style="color: red;">Denied</span>')
        else:
            return format_html('<span style="color: orange;">{0}%</span>', clearance.progress_percentage)
    clearance_status.short_description = 'Current Clearance'

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" />', obj.profile_picture.url)
        return "-"
    profile_picture_preview.short_description = 'Profile Picture'

    def approve_students(self, request, queryset):
        for student in queryset:
            student.approve_student(request.user)
        self.message_user(request, f"{queryset.count()} student(s) have been approved.")
    approve_students.short_description = "Approve selected students"

    def reject_students(self, request, queryset):
        # This would typically involve a form to collect the rejection reason
        # For simplicity, we're using a generic reason here
        for student in queryset:
            student.reject_student("Rejected through admin action")
        self.message_user(request, f"{queryset.count()} student(s) have been rejected.")
    reject_students.short_description = "Reject selected students"

    def export_students_data(self, request, queryset):
        # This would typically generate a CSV or Excel file
        # For now, we'll just show a message
        self.message_user(request, f"Data for {queryset.count()} student(s) would be exported.")
    export_students_data.short_description = "Export selected students data"

@admin.register(ClearanceRequest)
class ClearanceRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'office', 'school_year', 'semester', 'status', 'reviewed_by',
                   'request_date', 'reviewed_date', 'view_notes')
    list_filter = ('status', 'office', 'school_year', 'semester', 'request_date')
    search_fields = ('student__student_id', 'student__user__username', 'student__user__first_name',
                    'student__user__last_name', 'office__name', 'notes')
    raw_id_fields = ('student', 'office', 'clearance', 'reviewed_by')
    readonly_fields = ('request_date', 'reviewed_date')
    date_hierarchy = 'request_date'
    actions = ['approve_requests', 'deny_requests']

    def view_notes(self, obj):
        if obj.notes:
            return format_html('<span title="{0}">{1}...</span>',
                             obj.notes,
                             obj.notes[:30] + '...' if len(obj.notes) > 30 else obj.notes)
        return "-"
    view_notes.short_description = 'Notes'

    def approve_requests(self, request, queryset):
        # This is simplified - in a real scenario, you'd need to check permissions
        count = 0
        for req in queryset.filter(status='pending'):
            try:
                # Assuming the admin user has a staff profile
                staff = Staff.objects.filter(user=request.user).first()
                if staff:
                    req.approve(staff)
                    count += 1
            except Exception as e:
                self.message_user(request, f"Error approving request: {e}", level='error')

        self.message_user(request, f"{count} request(s) have been approved.")
    approve_requests.short_description = "Approve selected requests"

    def deny_requests(self, request, queryset):
        # This would typically involve a form to collect the denial reason
        # For simplicity, we're using a generic reason here
        count = 0
        for req in queryset.filter(status='pending'):
            try:
                staff = Staff.objects.filter(user=request.user).first()
                if staff:
                    req.deny(staff, "Denied through admin action")
                    count += 1
            except Exception as e:
                self.message_user(request, f"Error denying request: {e}", level='error')

        self.message_user(request, f"{count} request(s) have been denied.")
    deny_requests.short_description = "Deny selected requests"

@admin.register(Clearance)
class ClearanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'school_year', 'semester', 'is_cleared', 'program_chair_approved',
                   'cleared_date', 'progress_bar', 'created_at')
    list_filter = ('is_cleared', 'program_chair_approved', 'school_year', 'semester')
    search_fields = ('student__student_id', 'student__user__username', 'student__user__first_name',
                    'student__user__last_name')
    raw_id_fields = ('student',)
    readonly_fields = ('cleared_date', 'created_at')
    date_hierarchy = 'created_at'
    inlines = [ClearanceRequestInline]
    actions = ['approve_program_chair', 'check_clearance_status']

    def progress_bar(self, obj):
        if obj.total_requests == 0:
            return "No requests"

        percentage = obj.progress_percentage
        color = 'green' if percentage == 100 else 'orange' if percentage > 50 else 'red'

        return format_html(
            '<div style="width:100px; border:1px solid #ccc;">' +
            '<div style="width:{0}%; background-color:{1}; color:#fff; text-align:center;">' +
            '{0}%</div></div>', percentage, color)
    progress_bar.short_description = 'Progress'

    def approve_program_chair(self, request, queryset):
        count = 0
        for clearance in queryset:
            if clearance.is_cleared and not clearance.program_chair_approved:
                clearance.program_chair_approved = True
                clearance.save()
                count += 1

        self.message_user(request, f"{count} clearance(s) have been approved by program chair.")
    approve_program_chair.short_description = "Approve selected clearances by program chair"

    def check_clearance_status(self, request, queryset):
        for clearance in queryset:
            clearance.check_clearance()

        self.message_user(request, f"Status checked for {queryset.count()} clearance(s).")
    check_clearance_status.short_description = "Check clearance status"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_email', 'profile_picture_preview')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    raw_id_fields = ('user',)

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" />', obj.profile_picture.url)
        return "-"
    profile_picture_preview.short_description = 'Profile Picture'
