from django.core.management.base import BaseCommand
from core.models import ProgramChair

class Command(BaseCommand):
    help = 'Update existing program chairs with designations based on their dean'

    def handle(self, *args, **options):
        program_chairs = ProgramChair.objects.all()
        updated_count = 0

        for pc in program_chairs:
            if pc.dean and not pc.designation:
                pc.designation = pc.dean.name
                pc.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"Updated {pc.user.get_full_name()} with designation: {pc.designation}"
                ))

        self.stdout.write(self.style.SUCCESS(
            f"Updated {updated_count} program chairs with designations."
        ))
