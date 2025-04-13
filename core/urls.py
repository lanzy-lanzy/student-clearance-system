from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Basic Routes
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),

    # Student Routes
    path('profile/', views.student_profile, name='student_profile'),
    path('profile/update-picture/', views.update_profile_picture, name='update_profile_picture'),
    path('profile/update-contact/', views.update_contact_number, name='update_contact_number'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/create-clearance-requests/', views.create_clearance_requests, name='create_clearance_requests'),
    path('student/clearance/<int:clearance_id>/', views.view_clearance_details, name='view_clearance_details'),
    path('student/clearance-history/', views.student_clearance_history, name='student_clearance_history'),
    path('request-again/<int:request_id>/', views.request_again, name='request_again'),

    # Program Chair Routes
    path('program-chair/dashboard/', views.program_chair_dashboard, name='program_chair_dashboard'),
    path('program-chair/students/', views.ManageStudentsView.as_view(), name='manage_students'),
    path('program-chair/students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('program-chair/print-permit/<int:student_id>/', views.print_permit, name='print_permit'),
    path('program-chair/batch-print-permits/', views.batch_print_permits, name='batch_print_permits'),
    path('profile/program-chair/', views.program_chair_profile, name='program_chair_profile'),
    path('clearance/<int:clearance_id>/delete/', views.delete_clearance, name='delete_clearance'),

    # Staff Routes
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/pending-requests/', views.staff_pending_requests, name='staff_pending_requests'),
    path('staff/clearance-history/', views.staff_clearance_history, name='staff_clearance_history'),
    path('staff/profile/', views.staff_profile, name='staff_profile'),
    path('staff/view-request/<int:request_id>/', views.view_request, name='view_request'),
    path('approve-clearance-request/<int:request_id>/', views.approve_clearance_request, name='approve_clearance_request'),
    path('deny-clearance-request/<int:request_id>/', views.deny_clearance_request, name='deny_clearance_request'),
    path('clearance-request/<int:request_id>/update/', views.update_clearance_request, name='update_clearance_request'),

    # Dormitory Owner Routes
    path('dormitory-owner/dashboard/', views.bh_owner_dashboard, name='bh_owner_dashboard'),
    path('dormitory-owner/boarders/', views.bh_owner_boarders, name='bh_owner_boarders'),
    path('dormitory-owner/add-student/', views.bh_owner_add_student, name='bh_owner_add_student'),
    path('dormitory-owner/pending-requests/', views.bh_owner_pending_requests, name='bh_owner_pending_requests'),
    path('dormitory-owner/approved-requests/', views.bh_owner_approved_requests, name='bh_owner_approved_requests'),
    path('dormitory-owner/denied-requests/', views.bh_owner_denied_requests, name='bh_owner_denied_requests'),
    path('dormitory-owner/clearance-history/', views.bh_owner_clearance_history, name='bh_owner_clearance_history'),
    path('dormitory-owner/generate-reports/', views.bh_owner_generate_reports, name='bh_owner_generate_reports'),
    path('dormitory-owner/export-data/', views.bh_owner_export_data, name='bh_owner_export_data'),
    path('dormitory-owner/profile/', views.bh_owner_profile, name='bh_owner_profile'),

    # Admin Routes
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/users/', views.admin_users, name='admin_users'),
    path('dashboard/admin/offices/', views.admin_offices, name='admin_offices'),
    path('dashboard/admin/clearances/', views.admin_clearances, name='admin_clearances'),
    path('dashboard/admin/clearances/<int:clearance_id>/', views.clearance_details, name='clearance_details'),
    path('dashboard/admin/deans/', views.admin_deans, name='admin_deans'),
    path('dashboard/admin/deans/reassign/<int:dean_id>/', views.admin_reassign_courses, name='admin_reassign_courses'),
    path('dashboard/admin/courses/', views.admin_courses, name='admin_courses'),
    path('dashboard/admin/reassign-students/', views.admin_reassign_students, name='admin_reassign_students'),
    path('dashboard/admin/students/', views.admin_students, name='admin_students'),
    path('dashboard/admin/staff/', views.admin_staff, name='admin_staff'),
    path('dashboard/admin/staff/add/', views.admin_staff_add, name='admin_staff_add'),
    path('dashboard/admin/staff/<int:staff_id>/edit/', views.admin_staff_edit, name='admin_staff_edit'),
    path('dashboard/admin/settings/', views.admin_settings, name='admin_settings'),
    path('dashboard/admin/pending-approvals/', views.admin_pending_approvals, name='admin_pending_approvals'),
    path('dashboard/admin/program-chairs/', views.admin_program_chairs, name='admin_program_chairs'),
    path('dashboard/admin/dormitory-owners/', views.admin_dormitory_owners, name='admin_dormitory_owners'),
    path('dashboard/admin/reports/', views.admin_reports, name='admin_reports'),
    path('dashboard/create/users/', views.create_user, name='create_user'),
    path('profile/admin/', views.admin_profile, name='admin_profile'),

    path('dashboard/admin/approve-student/<int:student_id>/', views.approve_student, name='approve_student'),
    path('dashboard/admin/reject-student/<int:student_id>/', views.reject_student, name='reject_student'),
    # Report Routes
    path('generate-reports/', views.generate_reports, name='generate_reports'),
    path('generate-report/', views.generate_report, name='generate_report'),
    path('export-clearances-excel/', views.export_clearances_excel, name='export_clearances_excel'),

    # API Routes
    path('api/deans/<int:dean_id>/', views.get_dean_details, name='get_dean_details'),
    path('api/offices/detail/<int:office_id>/', views.office_detail_api, name='office_detail_api'),
    path('api/staff/<int:staff_id>/delete/', views.delete_staff, name='api_staff_delete'),
    path('dashboard/admin/student-details/<int:student_id>/', views.get_student_details, name='get_student_details'),
    # Add missing stats endpoint (example)
    path('dashboard/admin/get-approval-stats/', views.get_approval_stats, name='get_approval_stats'),
    path('api/courses-by-dean/<str:dean_name>/', views.get_courses_by_dean, name='courses_by_dean'),
    path('api/program-chairs/<int:dean_id>/', views.get_program_chairs, name='get_program_chairs'),

    # Dormitory Owner API Routes
    path('dashboard/admin/dormitory-owners/details/<int:owner_id>/', views.get_dormitory_owner_details, name='get_dormitory_owner_details'),
    path('dashboard/admin/dormitory-owners/unassigned-students/', views.get_unassigned_students, name='get_unassigned_students'),
    path('dashboard/admin/dormitory-owners/unassign-student/', views.unassign_student, name='unassign_student'),
    path('dashboard/admin/dormitory-owners/assign-students/', views.assign_students, name='assign_students'),
    path('api/program-chair/<int:program_chair_id>/', views.get_program_chair_details, name='get_program_chair_details'),
    path('api/courses/<int:dean_id>/', views.get_courses, name='get_courses'),  # Remove any login_required decorator
    path('api/courses/details/<int:course_id>/', views.get_course_details, name='get_course_details'),

    # Program Chair API Routes
    path('api/student/<int:student_id>/clearance-details/', api_views.student_clearance_details, name='api_student_clearance_details'),
    path('api/clearance/approve/', api_views.approve_clearance, name='api_approve_clearance'),
    path('api/clearance/deny/', api_views.deny_clearance, name='api_deny_clearance'),
    path('api/students/batch-details/', api_views.students_batch_details, name='api_students_batch_details'),
    path('api/batch-approval/<int:batch_id>/', api_views.batch_approval_details, name='api_batch_approval_details'),
    path('api/program-chair/reports/<str:report_type>/', api_views.program_chair_reports, name='api_program_chair_reports'),
    path('api/program-chair/reports/export/<str:format_type>/', api_views.export_program_chair_report, name='api_export_program_chair_report'),
]
