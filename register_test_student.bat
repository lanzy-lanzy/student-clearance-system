@echo off
echo Registering test student with contact number 639510440202...
python manage.py register_student --first_name "John" --last_name "Doe" --email "john.doe@example.com" --contact_number "639510440202" --course_code "BSCS" --year_level 2 --is_boarder --approved
pause
