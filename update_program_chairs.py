from django.core.management.base import BaseCommand
from core.models import ProgramChair

# Update existing program chairs with designations based on their dean
program_chairs = ProgramChair.objects.all()
updated_count = 0

for pc in program_chairs:
    if pc.dean and not pc.designation:
        pc.designation = pc.dean.name
        pc.save()
        updated_count += 1
        print(f"Updated {pc.user.get_full_name()} with designation: {pc.designation}")

print(f"Updated {updated_count} program chairs with designations.")
