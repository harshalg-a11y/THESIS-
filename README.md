# Thesis Portal

A feature-rich multi-portal thesis website with:
- Client portal
- Writer portal
- Admin portal
- Client–Writer messaging
- Thesis requests & milestones
- File uploads
- Notifications
- Analytics dashboard

## Setup

```bash
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## MySQL Setup

Create a database:
```sql
CREATE DATABASE thesis_portal;
```

Update `thesis_portal/settings.py` with your MySQL credentials.

## Run

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Go to:
- http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin
