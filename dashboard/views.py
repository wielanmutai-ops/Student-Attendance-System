from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def dashboard_redirect(request):
    user = request.user
    
    # Check if lecturer is approved
    if user.user_type == 'lecturer' and not user.is_approved:
        messages.error(request, 'Your account is pending approval by admin.')
        return redirect('logout')
    
    if user.user_type == 'admin':
        return redirect('admin_dashboard')
    elif user.user_type == 'lecturer':
        return redirect('lecturer_dashboard')
    elif user.user_type == 'student':
        return redirect('student_dashboard')
    
    return redirect('login')