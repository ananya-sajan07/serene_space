from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=191)  # 191 * 4 = 764 bytes < 767
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=20, default='user')
    phone = models.CharField(max_length=15, null = True, blank = True)
    place = models.CharField(max_length=100, null = True, blank = True)
    address = models.TextField(null = True, blank = True)
    gender = models.CharField(max_length = 100, null = True, blank = True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class MoodLog(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    mood = models.CharField(max_length=50)  # e.g., Happy, Sad, Stressed
    note = models.TextField(blank=True, null=True)  # optional user note
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.mood} ({self.created_at.date()})"


class Doctor(models.Model):
    status_choices = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(max_length = 100, unique = True)
    password = models.CharField(max_length = 100)
    qualification = models.CharField(max_length = 100, null = True, blank = True)
    specialization = models.CharField(max_length = 100, null = True, blank = True)
    experience = models.IntegerField(null = True, blank = True)
    hospital_name = models.CharField(max_length = 100, null = True, blank = True)
    hospital_address = models.TextField(null = True, blank = True)
    hospital_phone = models.CharField(max_length = 15, null = True, blank = True)
    latitude = models.DecimalField(max_digits = 9, decimal_places = 6, null = True, blank = True)
    longitude = models.DecimalField(max_digits = 9, decimal_places = 6, null = True, blank = True)
    role = models.CharField(max_length = 30, default = 'hospital_doctor')
    age = models.IntegerField(null = True, blank = True)
    gender = models.CharField(max_length = 100, null = True, blank = True)
    place = models.CharField(max_length = 100, null = True, blank = True)
    image = models.ImageField(upload_to = 'hospital_doctor_images/', null = True, blank = True)
    medical_id = models.ImageField(upload_to = 'hospital_medical_ids', null = True, blank = True)
    available = models.BooleanField(default = True)
    status = models.CharField(max_length = 20, choices=status_choices, default = 'pending')
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.name