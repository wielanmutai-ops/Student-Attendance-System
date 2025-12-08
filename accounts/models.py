from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import RegexValidator

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('lecturer', 'Lecturer'),
        ('student', 'Student'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    registration_number = models.CharField(max_length=20, blank=True, null=True, unique=True, verbose_name="Student Registration Number")
    employee_id = models.CharField(max_length=20, blank=True, null=True, unique=True, verbose_name="Lecturer/Staff ID")
    department = models.CharField(max_length=100, blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)  # For admin approval of lecturers
    
    # Remove student_id and lecturer_id fields since we're using registration_number and employee_id
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"
    
    def save(self, *args, **kwargs):
        # Auto-set email as username if not set
        if not self.username and self.email:
            self.username = self.email
        super().save(*args, **kwargs)

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    enrollment_date = models.DateField(default=timezone.now)
    semester = models.IntegerField(default=1)
    year_of_study = models.IntegerField(default=1)
    course = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.registration_number}"

class LecturerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lecturer_profile')
    qualification = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    office_location = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user.employee_id}"