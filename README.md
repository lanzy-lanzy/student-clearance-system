# Student Clearance System

A comprehensive Django-based system for managing student clearances in educational institutions.

## Features

- Student registration and approval system
- Dynamic clearance request and approval workflow
- Role-based access control (Admin, Staff, Program Chairs, Students)
- SMS notifications via Twilio integration
- PDF permit generation
- Comprehensive reporting and analytics
- Responsive UI with Tailwind CSS

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/student-clearance-system.git
cd student-clearance-system
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Populate initial data (optional):
```bash
python manage.py base_populate
```

7. Run the development server:
```bash
python manage.py runserver
```

## Usage

### Admin Dashboard

Access the admin dashboard at `/admin/dashboard/` to:
- Manage users, students, and staff
- Configure deans and program chairs
- View and manage clearance requests
- Generate reports

### Student Portal

Students can:
- Register and update their profile
- Submit clearance requests
- Track clearance status
- Download clearance permits

### Staff Portal

Staff members can:
- Review and approve/deny clearance requests
- Send notifications to students
- Generate reports for their office

## Configuration

### SMS Notifications

The system uses Twilio for SMS notifications. Configure your Twilio credentials in `core/utils.py`:

```python
TWILIO_ACCOUNT_SID = 'your-account-sid'
TWILIO_AUTH_TOKEN = 'your-auth-token'
TWILIO_PHONE_NUMBER = 'your-twilio-phone-number'
```

For Philippines numbers, the system follows Twilio's Philippines SMS guidelines. However, with a trial account, SMS to Philippines numbers will be simulated due to geographic restrictions. In production with a paid Twilio account, the system will send real SMS messages to all numbers.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
