from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'This command is deprecated. Required offices are created by data migrations.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('This command is deprecated.'))
        self.stdout.write(self.style.WARNING('Required offices (DORMITORY and PROGRAM CHAIR) are now created by data migrations.'))
        self.stdout.write(self.style.WARNING('Run `python manage.py migrate` to ensure the offices exist.'))
