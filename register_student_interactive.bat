@echo off
echo Student Registration Tool
echo ========================
echo.

set /p first_name="Enter first name: "
set /p last_name="Enter last name: "
set /p email="Enter email address: "
set /p contact_number="Enter contact number [639510440202]: "
if "%contact_number%"=="" set contact_number=639510440202

echo.
echo Available Courses:
python -c "from core.models import Course; print('\n'.join([f'  {c.code}: {c.name}' for c in Course.objects.all()]))"
echo.
set /p course_code="Enter course code: "

set /p year_level="Enter year level (1-5): "

set /p is_boarder="Is the student a boarder? (y/n): "
if /i "%is_boarder%"=="y" (
    set boarder_flag=--is_boarder
) else (
    set boarder_flag=
)

set /p auto_approve="Automatically approve the student? (y/n): "
if /i "%auto_approve%"=="y" (
    set approve_flag=--approved
) else (
    set approve_flag=
)

echo.
echo Registering student...
python manage.py register_student --first_name "%first_name%" --last_name "%last_name%" --email "%email%" --contact_number "%contact_number%" --course_code "%course_code%" --year_level %year_level% %boarder_flag% %approve_flag%

echo.
pause
