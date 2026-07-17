# Serene Space - Mental Health Platform

**Serene Space** is a comprehensive mental health web platform that connects users with doctors, provides mental health assessments (ADHD & Anxiety), offers a chatbot assistant, and manages appointments, prescriptions, and mood tracking.


## Features

### **For Users:**
- User registration & login
- Find and book appointments with doctors
- ADHD & Anxiety self-assessment using ML models
- Mood tracking with history
- AI-powered mental health chatbot (SereneBot)
- View prescriptions from doctors
- Leave reviews for doctors
- Browse mental health books

### **For Doctors:**
- Doctor registration (requires admin approval)
- Manage appointment bookings
- Set available time slots
- Issue prescriptions to patients
- Chat with patients
- View patient history

### **For Admin:**
- Admin dashboard with statistics
- Approve/reject doctor registrations
- Manage users, doctors, and books
- View all bookings
- Full CRUD operations

---

## Tech Stack

### Backend:
- **Django 5.2.8** - Python web framework
- **Django REST Framework** - RESTful API
- **MySQL** - Database
- **Channels** - WebSocket for real-time chat
- **Machine Learning** - ADHD & Anxiety prediction models (scikit-learn, joblib)

### Frontend:
- **HTML5 / CSS3** - Responsive UI
- **JavaScript** - Interactive elements
- **Bootstrap-like** custom dark theme

### APIs & Integrations:
- **Google Gemini API** - AI chatbot (SereneBot)
- **REST API** - Backend communication
- **WebSocket** - Real-time messaging

---

## Project Structure

```
backend/
├── adminapp/              # Admin panel & static pages
│   ├── templates/         # HTML templates
│   ├── views.py           # Admin views
│   └── urls.py            # Admin URLs
├── core/                  # Main application
│   ├── models.py          # Database models
│   ├── views.py           # API views
│   ├── serializers.py     # Data serializers
│   ├── consumers.py       # WebSocket consumers
│   ├── urls.py            # API URLs
│   ├── admin.py           # Django admin config
│   └── ml_models/         # ML prediction models
├── serene_backend/        # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py           # WebSocket configuration
├── manage.py
└── requirements.txt
```

---

## Installation & Setup

### Prerequisites:
- Python 3.8+
- MySQL
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/serene-space.git
cd serene-space
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```sql
-- Create MySQL database
CREATE DATABASE db_serenespace CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configure Settings
Update `backend/serene_backend/settings.py` with your database credentials:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'db_serenespace',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Admin User
```bash
python manage.py createsuperuser
```

### 8. Run Development Server
```bash
python manage.py runserver
```

Access the application:
- **User Portal:** http://127.0.0.1:8000/admin/user_auth/
- **Doctor Portal:** http://127.0.0.1:8000/admin/doctor_auth/
- **Admin Dashboard:** http://127.0.0.1:8000/admin/login/

---

## Default Admin Login
```
Email: admin@serenespace.com
Password: admin123
```

---

## Machine Learning Models

### ADHD Prediction
- Uses 12 features including age, gender, sleep patterns, and attention metrics
- Scikit-learn Random Forest model
- 85%+ accuracy

### Anxiety Prediction
- Uses 14 features from 7 categories
- Multi-class classification (No Anxiety, Anxiety, Bipolar Type 1, Bipolar Type 2)
- 90%+ accuracy

---

## Dependencies

```txt
Django==5.2.8
djangorestframework==3.15.2
mysqlclient==2.2.4
channels==4.1.0
google-generativeai==0.5.0
scikit-learn==1.4.1
joblib==1.3.2
numpy==1.26.4
django-cors-headers==4.3.1
reportlab==4.2.5
python-dotenv==1.0.1
```

---

## Screenshots

Admin Module - Manage Doctors Page
<img width="1880" height="819" alt="image" src="https://github.com/user-attachments/assets/d14b739c-365d-495b-b7ef-9b806adb9cb1" />

Doctor Module - Appointments Page
<img width="1265" height="819" alt="image" src="https://github.com/user-attachments/assets/1b9150ac-7dc1-4e47-ba1e-628e5065f358" />

User Module - Book Appointment Page
<img width="1415" height="840" alt="image" src="https://github.com/user-attachments/assets/e5cd72b7-b24e-46fd-834c-6e98f059e322" />

