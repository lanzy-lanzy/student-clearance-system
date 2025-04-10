# Admin Management Commands

This directory contains management commands to help with administrative tasks in the clearance system.

## Reassigning Students and Courses

When you need to delete a Dean or Course, you may encounter ProtectedError messages because of the relationships between Deans, Courses, and Students. These commands help you manage these relationships.

### reassign_students.py

Reassign students from one course to another.

```bash
# Basic usage
python manage.py reassign_students BSIT BSCS

# Dry run (show what would happen without making changes)
python manage.py reassign_students BSIT BSCS --dry-run
```

#### Arguments:
- `source_course_code`: Code of the source course (e.g., BSIT)
- `target_course_code`: Code of the target course (e.g., BSCS)
- `--dry-run`: Optional flag to show what would happen without making changes

### reassign_courses.py

Reassign courses from one dean to another.

```bash
# Basic usage
python manage.py reassign_courses "SET DEAN" "STE DEAN"

# Dry run (show what would happen without making changes)
python manage.py reassign_courses "SET DEAN" "STE DEAN" --dry-run
```

#### Arguments:
- `source_dean_name`: Name of the source dean (e.g., "SET DEAN")
- `target_dean_name`: Name of the target dean (e.g., "STE DEAN")
- `--dry-run`: Optional flag to show what would happen without making changes

## Deletion Process

To safely delete a Dean, you need to follow these steps:

1. Reassign all courses from the Dean to another Dean using the `reassign_courses` command or the admin interface.
2. Once all courses are reassigned, you can delete the Dean.

To safely delete a Course, you need to follow these steps:

1. Reassign all students from the Course to another Course using the `reassign_students` command or the admin interface.
2. Once all students are reassigned, you can delete the Course.

## Admin Interface

These operations can also be performed through the admin interface:

1. For Deans: Use the "Reassign courses to another dean" action.
2. For Courses: Use the "Reassign students to another course" action.

These actions provide a user-friendly interface for performing the same operations as the management commands.
