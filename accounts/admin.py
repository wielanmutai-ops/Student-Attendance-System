from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, LecturerProfile  # CORRECTED IMPORT

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_staff', 'is_approved')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_approved')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': (
            'user_type', 
            'registration_number', 
            'employee_id', 
            'department', 
            'phone_number', 
            'profile_picture',
            'is_approved'
        )}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': (
            'user_type', 
            'registration_number', 
            'employee_id', 
            'department', 
            'phone_number', 
            'profile_picture',
            'is_approved'
        )}),
    )

class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'enrollment_date', 'semester', 'year_of_study', 'course')
    list_filter = ('enrollment_date', 'semester', 'year_of_study')
    search_fields = ('user__first_name', 'user__last_name', 'user__registration_number', 'course')
    raw_id_fields = ('user',)

class LecturerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'qualification', 'specialization', 'office_location')
    list_filter = ('qualification',)
    search_fields = ('user__first_name', 'user__last_name', 'user__employee_id', 'specialization')
    raw_id_fields = ('user',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)  # CORRECTED
admin.site.register(LecturerProfile, LecturerProfileAdmin)  # CORRECTED