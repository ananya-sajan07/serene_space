from django.contrib import admin
from .models import User, MoodLog

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'created_at')
    search_fields = ('name', 'email')

@admin.register(MoodLog)
class MoodLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'mood', 'created_at')
    list_filter = ('mood', 'created_at')
    search_fields = ('user__name', 'note')
