from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=191)  # 191 * 4 = 764 bytes < 767
    password = models.CharField(max_length=100)
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