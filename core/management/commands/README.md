# Django Management Commands

This directory contains custom Django management commands for the clearance system.

## Available Commands

### base_populate.py

A flexible command for populating the database with test data. This command can be used to create basic structure, users, students, and clearance records.

#### Usage

```bash
# Basic usage (runs all operations with default settings)
python manage.py base_populate

# Create only users (admin, staff, program chairs)
python manage.py base_populate --users

# Create only students
python manage.py base_populate --students

# Create only clearance records
python manage.py base_populate --clearances

# Specify the number of records to create
python manage.py base_populate --count 10

# Specify school year and semester
python manage.py base_populate --school-year 2023-2024 --semester 1ST

# Combine options
python manage.py base_populate --users --students --count 20 --school-year 2023-2024 --semester 2ND
```

#### Options

- `--users`: Create basic users (admin, staff, program chairs)
- `--students`: Create sample students
- `--clearances`: Create clearance records for students
- `--count`: Number of sample records to create (default: 5)
- `--school-year`: School year in format YYYY-YYYY (default: current year)
- `--semester`: Semester (1ST, 2ND, or SUM) (default: 1ST)

### populate_data.py

The original data population command that creates a fixed set of sample data.

### create_program_chair.py

Creates program chair accounts.

### register_student.py

Registers new student accounts.

### student_data.py

Utility command for managing student data.

## Creating New Commands

To create a new management command:

1. Create a new Python file in this directory
2. Extend the `BaseCommand` class from Django
3. Implement the `handle` method
4. Make the command executable by running `python manage.py your_command_name`

Example:

```python
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Description of your command'

    def add_arguments(self, parser):
        # Add command line arguments if needed
        parser.add_argument('--example', type=str, help='Example argument')

    def handle(self, *args, **options):
        # Command implementation
        self.stdout.write(self.style.SUCCESS('Command executed successfully!'))
```
