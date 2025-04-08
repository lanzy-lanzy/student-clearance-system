import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clearance_version_control.settings')
django.setup()

from core.models import Student, Course

# List all courses
print("Available courses:")
for course in Course.objects.all():
    student_count = Student.objects.filter(course=course).count()
    print(f"ID: {course.id}, Code: {course.code}, Name: {course.name}, Students: {student_count}")

# Get the course you want to delete
course_to_delete_id = input("\nEnter ID of course to delete: ")
course_to_reassign_id = input("Enter ID of course to reassign students to: ")

try:
    course_to_delete = Course.objects.get(id=course_to_delete_id)
    course_to_reassign = Course.objects.get(id=course_to_reassign_id)
    
    # Find students in the course to delete
    students = Student.objects.filter(course=course_to_delete)
    
    if students.exists():
        print(f"\nFound {students.count()} students in {course_to_delete.code}:")
        for student in students:
            print(f"- {student}")
        
        confirm = input(f"\nReassign these students to {course_to_reassign.code}? (y/n): ")
        if confirm.lower() == 'y':
            # Reassign students
            for student in students:
                student.course = course_to_reassign
                student.save()
                print(f"Reassigned {student} to {course_to_reassign.code}")
            
            # Now delete the course
            course_to_delete.delete()
            print(f"\nSuccessfully deleted {course_to_delete.code}")
        else:
            print("Operation cancelled.")
    else:
        print(f"No students found in {course_to_delete.code}")
        delete_anyway = input("Delete this course? (y/n): ")
        if delete_anyway.lower() == 'y':
            course_to_delete.delete()
            print(f"Successfully deleted {course_to_delete.code}")
        else:
            print("Operation cancelled.")
            
except Course.DoesNotExist:
    print("One or both courses not found.")
except Exception as e:
    print(f"Error: {e}")
