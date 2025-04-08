# Student Registration Tools

This directory contains several tools to register students in the system.

## Django Management Command

The most flexible option is to use the Django management command:

```bash
python manage.py register_student --first_name "John" --last_name "Doe" --email "john.doe@example.com" --contact_number "639510440202" --course_code "BSCS" --year_level 2 --is_boarder --approved
```

### Available Options

- `--first_name`: First name of the student (required)
- `--last_name`: Last name of the student (required)
- `--email`: Email address of the student (required)
- `--contact_number`: Contact number of the student (default: 639510440202)
- `--course_code`: Course code (must exist in the database) (required)
- `--year_level`: Year level (1-5) (required)
- `--is_boarder`: Whether the student is a boarder (flag, no value needed)
- `--password`: Password for the student account (optional, will be generated if not provided)
- `--approved`: Whether to automatically approve the student (flag, no value needed)

## Batch Files

### Simple Test Registration

Run `register_test_student.bat` to register a test student with predefined values.

### Interactive Registration

Run `register_student_interactive.bat` to be prompted for each value.

## Python Script

For programmatic use, you can import and use the `register_student.py` script:

```python
from register_student import register_student

student = register_student(
    first_name="John",
    last_name="Doe",
    email="john.doe@example.com",
    contact_number="639510440202",
    course_code="BSCS",  # Replace with an actual course code from your database
    year_level=2,
    is_boarder=True,
    approved=True
)
```

## Notes

- The contact number will be automatically formatted to E.164 format (e.g., +639510440202)
- If a course code doesn't exist, the command will show available courses
- Student IDs are automatically generated based on name and current year
- Usernames are generated from first and last name
- Passwords are randomly generated if not provided
