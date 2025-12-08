from django import forms
from django.utils import timezone
from .models import Level, Course, Unit, AttendanceSession, AttendanceReport
from accounts.models import LecturerProfile, StudentProfile, User


class LevelForm(forms.ModelForm):
    class Meta:
        model = Level
        fields = ['year', 'semester', 'is_active']  
        
    def clean(self):
        cleaned_data = super().clean()
        year = cleaned_data.get('year')
        semester = cleaned_data.get('semester')
        
        # Check if this year/semester combination already exists
        if Level.objects.filter(year=year, semester=semester).exists():
            if self.instance and self.instance.pk:
                if not (self.instance.year == year and self.instance.semester == semester):
                    raise forms.ValidationError(
                        f"Year {year} Semester {semester} already exists."
                    )
            else:
                raise forms.ValidationError(
                    f"Year {year} Semester {semester} already exists."
                )
        
        return cleaned_data


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'level', 'duration_years', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter course name'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'duration_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        # CHANGED: 'lecturer' → 'lecturers' (ManyToManyField)
        fields = ['code', 'name', 'description', 'course', 'academic_level', 'academic_year', 'is_core', 'lecturers', 'credit_hours']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CS101'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Introduction to Programming'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Unit description...'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'academic_level': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2024/2025'}),
            'lecturers': forms.SelectMultiple(attrs={'class': 'form-select', 'multiple': True}),  # CHANGED: Select → SelectMultiple
            'credit_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 6}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show ALL courses
        self.fields['course'].queryset = Course.objects.all().order_by('code')
        
        # Only show active academic levels
        self.fields['academic_level'].queryset = Level.objects.filter(is_active=True).order_by('year', 'semester')
        
        # Only show approved lecturers - CHANGED: lecturer → lecturers
        approved_lecturers = User.objects.filter(
            user_type='lecturer',
            is_approved=True
        )
        self.fields['lecturers'].queryset = LecturerProfile.objects.filter(user__in=approved_lecturers)


class UnitAssignmentForm(forms.Form):
    """Form for assigning multiple units to multiple lecturers"""
    # CHANGED: ModelChoiceField → ModelMultipleChoiceField, lecturer → lecturers
    lecturers = forms.ModelMultipleChoiceField(
        queryset=LecturerProfile.objects.none(),
        required=True,
        label="Select Lecturers",
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'multiple': True})
    )
    # CHANGED: Show all units, not just unassigned ones
    units = forms.ModelMultipleChoiceField(
        queryset=Unit.objects.all(),
        required=True,
        label="Select Units to Assign",
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter approved lecturers
        approved_lecturers = User.objects.filter(
            user_type='lecturer',
            is_approved=True
        )
        self.fields['lecturers'].queryset = LecturerProfile.objects.filter(
            user__in=approved_lecturers
        ).order_by('user__first_name')


class AttendanceSessionForm(forms.ModelForm):
    class Meta:
        model = AttendanceSession
        fields = ['unit', 'session_date', 'start_time', 'end_time', 'location', 'session_type', 'delivery_mode']
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'session_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Room 101, Building A'}),
            'session_type': forms.Select(attrs={'class': 'form-select'}),
            'delivery_mode': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, lecturer=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if lecturer:
            self.fields['unit'].queryset = Unit.objects.filter(lecturers=lecturer).order_by('code')
   
        self.fields['session_type'].choices = [
            ('', '-- Select Session Type --'),
            ('normal', 'Normal Class'),
            ('makeup', 'Make-up Class'),
            ('extra', 'Extra Class'),
            ('exam', 'Exam Session'),
        ]
        
        self.fields['delivery_mode'].choices = [
            ('', '-- Select Delivery Mode --'),
            ('physical', 'Physical/In-person'),
            ('virtual', 'Virtual/Online'),
            ('hybrid', 'Hybrid'),
        ]

class AttendanceCodeForm(forms.Form):
    attendance_code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter 6-digit code',
            'class': 'form-control',
            'autocomplete': 'off'
        })
    )


class AttendanceReportForm(forms.ModelForm):
    class Meta:
        model = AttendanceReport
        fields = ['admin_notes']
        widgets = {
            'admin_notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }