from django.db import models

class SereneAdmin(models.Model):
    Email = models.EmailField(max_length=191, unique=True)  # 191 chars for MySQL
    password = models.CharField(max_length=200)
    
    def __str__(self):
        return self.Email