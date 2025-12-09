from django.contrib import admin

from .models import SereneAdmin, tbl_hospital_doctor_register

@admin.register(tbl_hospital_doctor_register)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'specialization', 'status', 'created_at')
    list_filter = ('status', 'specialization')
    search_fields = ('name', 'email', 'hospital_name')
admin.site.register(SereneAdmin)