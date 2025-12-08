from django.urls import path
from django.shortcuts import redirect
from accounts.views import profile_view

def dashboard_redirect(request):
    user = request.user
    if user.is_authenticated:
        if user.user_type == 'admin':
            return redirect('admin_dashboard')
        elif user.user_type == 'lecturer':
            return redirect('lecturer_dashboard')
        elif user.user_type == 'student':
            return redirect('student_dashboard')
    return redirect('login')

urlpatterns = [
    path('', dashboard_redirect, name='dashboard'),
    path('profile/', profile_view, name='profile'),
]