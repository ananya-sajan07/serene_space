# Django Administration Configuration for Core App Models
# This file registers core app models with Django's built-in admin interface
# Models registered here will appear at /django-admin/ 

from django.contrib import admin
from .models import User, Doctor, Book, MoodLog # Import the Book model just created

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'created_at')
    search_fields = ('name', 'email')

@admin.register(Book) # Decorator: Registers Book model with Django admin
class BookAdmin(admin.ModelAdmin):# Creates admin configuration for Book
    list_display = ['title', 'author', 'category', 'is_active', 'created_at'] # Which columns to show in the admin list view: | Shows: Title | Author | Category | Active? | Created Date
    list_filter = ['category', 'is_active'] # Adds filters on right sidebar: | Filter by: Category (ADHD/Depression/General) and Active status
    search_fields = ['title', 'author', 'description'] # Adds search box that searches in title, author, and description fields

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'specialization', 'status', 'available', 'created_at')
    list_filter = ('status', 'available', 'specialization')
    search_fields = ('name', 'email', 'hospital_name')    

@admin.register(MoodLog)
class MoodLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'mood', 'created_at')
    list_filter = ('mood', 'created_at')
    search_fields = ('user__name', 'note')
