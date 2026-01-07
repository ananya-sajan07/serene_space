# Django Administration Configuration for Core App Models
# This file registers core app models with Django's built-in admin interface
# Models registered here will appear at /django-admin/ 

from django.contrib import admin
from django import forms
from .models import User, Doctor, TimeSlot, Book, Booking, DoctorFeedback, MoodLog 

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

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'date', 'get_start_time', 'get_end_time', 'is_booked', 'created_at']
    list_filter = ['date', 'is_booked', 'doctor']
    search_fields = ['doctor__name']
    
    def get_start_time(self, obj):
        return obj.slot_data.get('start_time', 'N/A')
    get_start_time.short_description = 'Start Time'
    
    def get_end_time(self, obj):
        return obj.slot_data.get('end_time', 'N/A')
    get_end_time.short_description = 'End Time'
    
    # Customize form field for slot_data
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'slot_data':
            field.help_text = 'Enter as JSON: {"start_time": "14.00", "end_time": "15.00"}'
            field.widget = forms.Textarea(attrs={'rows': 3, 'cols': 50})
        return field  

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'doctor', 'time_slot', 'status', 'created_at']
    list_filter = ['status', 'doctor', 'user']
    search_fields = ['user__name', 'doctor__name']

@admin.register(DoctorFeedback)
class DoctorFeedbackAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'doctor']
    search_fields = ['doctor__name', 'user__name', 'comment']
    
@admin.register(MoodLog)
class MoodLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'mood', 'created_at')
    list_filter = ('mood', 'created_at')
    search_fields = ('user__name', 'note')
