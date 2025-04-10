from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Student, Course


class Command(BaseCommand):
    help = 'Reassign students from one course to another'

    def add_arguments(self, parser):
        parser.add_argument('source_course_code', type=str, help='Code of the source course')
        parser.add_argument('target_course_code', type=str, help='Code of the target course')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')

    def handle(self, *args, **options):
        source_code = options['source_course_code']
        target_code = options['target_course_code']
        dry_run = options.get('dry_run', False)

        try:
            source_course = Course.objects.get(code=source_code)
        except Course.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Source course '{source_code}' does not exist"))
            return

        try:
            target_course = Course.objects.get(code=target_code)
        except Course.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Target course '{target_code}' does not exist"))
            return

        if source_course == target_course:
            self.stdout.write(self.style.ERROR("Source and target courses cannot be the same"))
            return

        students = Student.objects.filter(course=source_course)
        count = students.count()

        if count == 0:
            self.stdout.write(self.style.WARNING(f"No students found in course '{source_code}'"))
            return

        self.stdout.write(self.style.SUCCESS(f"Found {count} students in course '{source_code}'"))
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"DRY RUN: Would reassign {count} students from '{source_code}' to '{target_code}'"))
            for student in students:
                self.stdout.write(f"  - {student.student_id}: {student.get_full_name()}")
            return

        try:
            with transaction.atomic():
                updated = students.update(course=target_course)
                self.stdout.write(self.style.SUCCESS(f"Successfully reassigned {updated} students from '{source_code}' to '{target_code}'"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reassigning students: {e}"))
