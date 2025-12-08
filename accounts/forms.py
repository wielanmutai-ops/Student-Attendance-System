from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User

class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your first name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your last name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your email address'})
    )
    registration_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your registration number'})
    )
    department = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your department'})
    )
    phone_number = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter phone number (optional)'})
    )
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 
            'registration_number', 'department', 
            'phone_number', 'password1', 'password2'
        ]
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email
    
    def clean_registration_number(self):
        reg_number = self.cleaned_data.get('registration_number')
        if User.objects.filter(registration_number=reg_number).exists():
            raise ValidationError("This registration number is already registered.")
        return reg_number
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'  # Force student type
        user.username = self.cleaned_data['email']  # Use email as username
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter email or username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )

class LecturerCreationForm(UserCreationForm):
    """Form for admin to create lecturer accounts"""
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 
            'employee_id', 'department', 'phone_number',
            'is_approved'
        ]
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'lecturer'
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user