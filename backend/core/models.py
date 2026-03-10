from django.db import models
import json

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
    hospital_phone   = models.CharField(max_length = 15, null = True, blank = True)
    latitude         = models.DecimalField(max_digits = 9, decimal_places = 6, null = True, blank = True)
    longitude        = models.DecimalField(max_digits = 9, decimal_places = 6, null = True, blank = True)
    role             = models.CharField(max_length = 30, default = 'hospital_doctor')
    age = models.IntegerField(null = True, blank = True)
    gender     = models.CharField(max_length = 100, null = True, blank = True)
    place =      models.CharField(max_length = 100, null = True, blank = True)
    image = models.ImageField(upload_to = 'hospital_doctor_images/', null = True, blank = True)
    medical_id = models.ImageField(upload_to = 'hospital_medical_ids', null = True, blank = True)
    available = models.BooleanField(default = False)
    status = models.CharField(max_length = 20, choices=status_choices, default = 'pending')
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.name
    
class Book(models.Model):
    CATEGORY_CHOICES = [  # Creates dropdown options for category field
        ('adhd', 'ADHD'), #'database value', 'display value'
        ('depression', 'DEPRESSION'),
        ('anxiety', 'ANXIETY'),
        ('general', 'General Mental Health'),
    ]

    title       = models.CharField(max_length = 200)
    author      = models.CharField(max_length=100)
    category    = models.CharField(max_length=20, choices=CATEGORY_CHOICES) # Stores category as 'adhd', 'depression', or 'general'. Shows as dropdown in forms
    description = models.TextField() # Long description, no length limit
    cover_image = models.ImageField(upload_to='book_covers/', null = True, blank = True) # Stores book cover images in 'book_covers/' folder | null=True: Can be empty in database. | blank=True: Can be empty in forms
    is_active   = models.BooleanField(default=True) # True = book is visible to users | False = book is hidden (soft delete)
    created_at  = models.DateTimeField(auto_now_add = True) # Automatically sets date when book is created

    def __str__(self):
        return f"{self.title} - {self.get_category_display()}" # Shows "Book Title - ADHD" in admin panel instead of "Book object (1)"

class TimeSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()  # Date for which slots are available
    slot_data = models.JSONField()  # Stores {"slots": ["9.00", "10.00", "11.00", "14.00", "15.00"]}
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        slots = self.slot_data.get('slots', [])
        return f"{self.doctor.name} - {self.date} ({', '.join(slots)})"

class DoctorFeedback(models.Model):
    #User feedback/review for doctors

    RATING_CHOICES = [
        (1, '1 Star - Poor'),
        (2, '2 Stars - Fair'),
        (3, '3 Stars - Good'),
        (4, '4 Stars - Very Good'),
        (5, '5 Stars - Excellent'),
    ]

    doctor     = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name = 'feedbacks')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_feedbacks')
    rating     = models.IntegerField(choices=RATING_CHOICES)
    comment    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} -> {self.doctor.name}: {self.rating} stars"
    
    class Meta:
        #A user can give only one feedback per doctor
        unique_together = ['doctor', 'user']

class Booking(models.Model):
    #User booking for doctor's time slot

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    doctor     = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='bookings')
    time_slot  = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='bookings')
    booked_time = models.CharField(max_length=10, null=True, blank=True)
    status     = models.CharField(max_length=20,choices=STATUS_CHOICES, default='pending')
    symptoms   = models.TextField(blank=True, null=True) #User can describe symptoms
    notes      = models.TextField(blank=True, null=True) #Additional Notes
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.name} booked {self.doctor.name} at {self.booked_time} on {self.time_slot.date}"

class MoodLog(models.Model):
    user       = models.ForeignKey('User', on_delete=models.CASCADE)
    mood       = models.CharField(max_length=50)  # e.g., Happy, Sad, Stressed
    note       = models.TextField(blank=True, null=True)  # optional user note
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.mood} ({self.created_at.date()})"

class AssessmentResult(models.Model):
    ASSESSMENT_TYPES = [
        ('adhd', 'ADHD Assessment'),
        ('anxiety', 'Anxiety Assessment'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessments')
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    result = models.CharField(max_length=100)  # e.g., "ADHD", "No ADHD", "YES", "Bipolar Type 1"
    confidence = models.FloatField()  # confidence score 0-1
    details = models.JSONField(null=True, blank=True)  # store all input features and probabilities
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.name} - {self.get_assessment_type_display()} - {self.result} ({self.created_at.date()})"