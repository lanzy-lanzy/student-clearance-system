import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clearance.settings')
django.setup()

from core.models import Student

def main():
    # Get all pending students with the specific contact number
    pending_students = Student.objects.filter(
        contact_number='+639510440202',
        is_approved=False
    ).order_by('-created_at')
    
    print(f"Total pending students with contact number +639510440202: {pending_students.count()}")
    print("\nPending students:")
    print("-" * 80)
    print(f"{'ID':<15} {'Name':<30} {'Student ID':<15} {'Course':<10} {'Year':<5}")
    print("-" * 80)
    
    for i, student in enumerate(pending_students, 1):
        full_name = f"{student.user.first_name} {student.user.last_name}"
        print(f"{i:<15} {full_name:<30} {student.student_id:<15} {student.course.code:<10} {student.year_level}")
    
    print("-" * 80)
    print("\nThese students are ready for approval in the admin panel.")
    print("You can approve them at: http://127.0.0.1:8000/dashboard/admin/pending_approvals/")

if __name__ == "__main__":
    main()
