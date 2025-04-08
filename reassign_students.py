import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clearance_version_control.settings')
django.setup()

from core.models import Student, Course

def reassign_students_and_delete_course(old_course_id, new_course_id):
    """
    Reassign all students from one course to another, then delete the old course.
    
    Args:
        old_course_id: ID of the course to be deleted
        new_course_id: ID of the course to reassign students to
    """
    try:
        old_course = Course.objects.get(id=old_course_id)
        new_course = Course.objects.get(id=new_course_id)
        
        # Get all students in the old course
        students = Student.objects.filter(course=old_course)
        student_count = students.count()
        
        if student_count == 0:
            print(f"No students found in course {old_course.code} - {old_course.name}")
            old_course.delete()
            print(f"Course {old_course.code} - {old_course.name} deleted successfully.")
            return
        
        # Print students to be reassigned
        print(f"Found {student_count} students in course {old_course.code} - {old_course.name}:")
        for student in students:
            print(f"  - {student}")
        
        # Confirm reassignment
        confirm = input(f"Reassign these {student_count} students to {new_course.code} - {new_course.name}? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return
        
        # Reassign students
        for student in students:
            student.course = new_course
            student.save()
            print(f"Reassigned {student} to {new_course.code} - {new_course.name}")
        
        # Delete the old course
        old_course.delete()
        print(f"Course {old_course.code} - {old_course.name} deleted successfully.")
        
    except Course.DoesNotExist as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # List all courses
    print("Available courses:")
    for course in Course.objects.all():
        student_count = Student.objects.filter(course=course).count()
        print(f"ID: {course.id}, Code: {course.code}, Name: {course.name}, Students: {student_count}")
    
    # Get course IDs from user
    old_course_id = input("\nEnter ID of course to delete: ")
    new_course_id = input("Enter ID of course to reassign students to: ")
    
    # Convert to integers
    try:
        old_course_id = int(old_course_id)
        new_course_id = int(new_course_id)
        
        # Make sure they're not the same
        if old_course_id == new_course_id:
            print("Error: Cannot reassign to the same course.")
        else:
            reassign_students_and_delete_course(old_course_id, new_course_id)
    except ValueError:
        print("Error: Course IDs must be integers.")
