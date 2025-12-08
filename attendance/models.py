from django.db import models
from django.utils import timezone
import random
import string
from accounts.models import User, StudentProfile, LecturerProfile  # Updated import

# ==================== NEW MODELS ====================

# models.py - Level model
class Level(models.Model):
    year = models.PositiveIntegerField(choices=[(1, 'Year 1'), (2, 'Year 2'), (3, 'Year 3'), (4, 'Year 4'), (5, 'Year 5')])
    semester = models.PositiveIntegerField(choices=[(1, 'Semester 1'), (2, 'Semester 2'), (3, 'Semester 3')])
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=100, blank=True)
    
    def save(self, *args, **kwargs):
        self.name = f"Year {self.year} Semester {self.semester}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Year {self.year} Semester {self.semester}"
    
    class Meta:
        ordering = ['year', 'semester']
        unique_together = ['year', 'semester']  

# models.py - Add this to Course model
class Course(models.Model):
    code = models.CharField(max_length=20, blank=True)  # ADD THIS LINE
    name = models.CharField(max_length=200)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='courses')
    duration_years = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        # Auto-generate code if empty
        if not self.code:
            words = self.name.split()
            if words:
                initials = ''.join(word[0].upper() for word in words if word)
                self.code = f"{initials[:4]}{random.randint(100, 999)}"
            else:
                self.code = f"CRS{random.randint(1000, 9999)}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.code} - {self.name} ({self.level})"

class Semester(models.Model):
    """Academic semesters: Year 1 Semester 1, Year 1 Semester 2, etc."""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='semesters')
    year = models.IntegerField(default=1, help_text="Academic year (1, 2, 3, etc.)")
    semester_number = models.IntegerField(default=1, help_text="Semester number (1 or 2)")
    name = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['course', 'year', 'semester_number']
        unique_together = ['course', 'year', 'semester_number']
    
    def save(self, *args, **kwargs):
        # Auto-generate name if not provided
        if not self.name:
            self.name = f"Year {self.year} Semester {self.semester_number}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.course.code} - {self.name}"

# ==================== UPDATED UNIT MODEL ====================

class Unit(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='units', null=True, blank=True)
    academic_level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True, related_name='units')
    # lecturer = models.ForeignKey(LecturerProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_units')
    lecturers = models.ManyToManyField(LecturerProfile, related_name='assigned_units', blank=True)
    students = models.ManyToManyField(StudentProfile, related_name='enrolled_units', blank=True)
    credit_hours = models.IntegerField(default=3)
    is_core = models.BooleanField(default=True, help_text="Core unit or elective")
    academic_year = models.CharField(max_length=10, blank=True, null=True)
    
    class Meta:
        ordering = ['course', 'academic_level__year', 'academic_level__semester', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

# ==================== EXISTING MODELS ====================

class AttendanceSession(models.Model):
    SESSION_TYPE_CHOICES = (
        ('normal', 'Normal Class'),
        ('makeup', 'Make-up Class'),
        ('extra', 'Extra Class'),
        ('exam', 'Exam Session'),
    )
    
    DELIVERY_MODE_CHOICES = (
        ('physical', 'Physical/In-person'),
        ('virtual', 'Virtual/Online'),
        ('hybrid', 'Hybrid'),
    )
    
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='sessions')
    lecturer = models.ForeignKey(LecturerProfile, on_delete=models.CASCADE)
    session_date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=100)
    
    # NEW FIELDS ADDED:
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, default='normal')
    delivery_mode = models.CharField(max_length=20, choices=DELIVERY_MODE_CHOICES, default='physical')
    
    attendance_code = models.CharField(max_length=6, unique=True, blank=True)
    code_generated_at = models.DateTimeField(null=True, blank=True)
    code_expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def generate_attendance_code(self):
        """Generate a 6-digit random code"""
        code = ''.join(random.choices(string.digits, k=6))
        self.attendance_code = code
        self.code_generated_at = timezone.now()
        # Code expires in 15 minutes
        self.code_expires_at = timezone.now() + timezone.timedelta(minutes=15)
        self.save()
        return code
    
    def is_code_valid(self):
        if not self.code_expires_at:
            return False
        return timezone.now() < self.code_expires_at and self.is_active
    
    def __str__(self):
        return f"{self.unit.code} - {self.session_date} ({self.session_type})"

class AttendanceRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_records')
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    marked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    location_data = models.JSONField(null=True, blank=True)
    marked_with_code = models.CharField(max_length=6)
    
    class Meta:
        unique_together = ['student', 'session']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.session}"

class AttendanceReport(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('submitted', 'Submitted to Admin'),
        ('reviewed', 'Reviewed by Admin'),
        ('rejected', 'Rejected'),
    )
    
    session = models.OneToOneField(AttendanceSession, on_delete=models.CASCADE, related_name='report')
    submitted_by = models.ForeignKey(LecturerProfile, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='attendance_reports/', null=True, blank=True)
    
    def __str__(self):
        return f"Report for {self.session} - {self.status}"
    