from django.core.management.base import BaseCommand
from core.models import Student
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Find and remove 5th year students from the system'

    def handle(self, *args, **options):
        # Find all 5th year students
        fifth_year_students = Student.objects.filter(year_level=5)
        count = fifth_year_students.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No 5th year students found in the system.'))
            return
        
        self.stdout.write(f'Found {count} 5th year students:')
        
        # Display the list of students to be removed
        for student in fifth_year_students:
            self.stdout.write(f'  - {student.student_id}: {student.user.get_full_name()} ({student.user.email})')
        
        # Confirm deletion
        self.stdout.write(self.style.WARNING('Are you sure you want to delete these students? This action cannot be undone.'))
        self.stdout.write('Type "yes" to confirm: ')
        
        confirm = input()
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.ERROR('Operation cancelled.'))
            return
        
        # Delete the students
        deleted_count = 0
        for student in fifth_year_students:
            try:
                # Get the user associated with the student
                user = student.user
                # Delete the user (this will cascade delete the student)
                user.delete()
                deleted_count += 1
                self.stdout.write(f'Deleted student: {student.student_id}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error deleting student {student.student_id}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} 5th year students.'))
