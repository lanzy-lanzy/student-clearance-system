from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Dean, Course, Student


class Command(BaseCommand):
    help = 'Reassign courses from one dean to another'

    def add_arguments(self, parser):
        parser.add_argument('source_dean_name', type=str, help='Name of the source dean')
        parser.add_argument('target_dean_name', type=str, help='Name of the target dean')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')

    def handle(self, *args, **options):
        source_name = options['source_dean_name']
        target_name = options['target_dean_name']
        dry_run = options.get('dry_run', False)

        try:
            source_dean = Dean.objects.get(name=source_name)
        except Dean.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Source dean '{source_name}' does not exist"))
            return

        try:
            target_dean = Dean.objects.get(name=target_name)
        except Dean.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Target dean '{target_name}' does not exist"))
            return

        if source_dean == target_dean:
            self.stdout.write(self.style.ERROR("Source and target deans cannot be the same"))
            return

        courses = Course.objects.filter(dean=source_dean)
        count = courses.count()

        if count == 0:
            self.stdout.write(self.style.WARNING(f"No courses found for dean '{source_name}'"))
            return

        self.stdout.write(self.style.SUCCESS(f"Found {count} courses for dean '{source_name}'"))
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"DRY RUN: Would reassign {count} courses from '{source_name}' to '{target_name}'"))
            for course in courses:
                student_count = Student.objects.filter(course=course).count()
                self.stdout.write(f"  - {course.code}: {course.name} ({student_count} students)")
            return

        try:
            with transaction.atomic():
                updated = courses.update(dean=target_dean)
                self.stdout.write(self.style.SUCCESS(f"Successfully reassigned {updated} courses from '{source_name}' to '{target_name}'"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reassigning courses: {e}"))
