from django.core.management.base import BaseCommand
from core.models import Office

class Command(BaseCommand):
    help = 'Ensures that required system offices exist in the database'

    def handle(self, *args, **options):
        # Ensure DORMITORY office exists
        if not Office.objects.filter(name='DORMITORY').exists():
            Office.objects.create(
                name='DORMITORY',
                office_type='OTHER',
                description='University Dormitory'
            )
            self.stdout.write(self.style.SUCCESS('Successfully created DORMITORY office'))
        else:
            self.stdout.write(self.style.SUCCESS('DORMITORY office already exists'))

        # Ensure PROGRAM CHAIR office exists
        if not Office.objects.filter(name='PROGRAM CHAIR').exists():
            Office.objects.create(
                name='PROGRAM CHAIR',
                office_type='OTHER',
                description='Program Chair Office'
            )
            self.stdout.write(self.style.SUCCESS('Successfully created PROGRAM CHAIR office'))
        else:
            self.stdout.write(self.style.SUCCESS('PROGRAM CHAIR office already exists'))
