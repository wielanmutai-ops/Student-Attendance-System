from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .forms import StudentRegistrationForm, LoginForm, LecturerCreationForm
from .models import User, StudentProfile, LecturerProfile

def register_view(request):
    """Only for student registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create student profile
            StudentProfile.objects.create(
                user=user,
                enrollment_date=timezone.now().date()
            )
            
            messages.success(request, 'Registration successful! You can now login.')
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    
    context = {
        'form': form,
        'title': 'Student Registration'
    }
    return render(request, 'accounts/register.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Check if lecturer is approved
                if user.user_type == 'lecturer' and not user.is_approved:
                    messages.error(request, 'Your account is pending approval by admin.')
                    return render(request, 'accounts/login.html', {'form': form})
                
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

# Admin only views for lecturer management
def admin_required(view_func):
    """Decorator to check if user is admin"""
    decorated_view_func = user_passes_test(
        lambda u: u.is_authenticated and u.user_type == 'admin',
        login_url='login'
    )(view_func)
    return decorated_view_func

@login_required
@admin_required
def create_lecturer_view(request):
    """Admin creates lecturer accounts"""
    if request.method == 'POST':
        form = LecturerCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create lecturer profile
            LecturerProfile.objects.create(user=user)
            
            messages.success(request, f'Lecturer account created for {user.get_full_name()}')
            return redirect('manage_lecturers')
    else:
        form = LecturerCreationForm()
    
    return render(request, 'accounts/create_lecturer.html', {'form': form})

@login_required
@admin_required
def manage_lecturers_view(request):
    """Admin manages lecturer accounts"""
    lecturers = User.objects.filter(user_type='lecturer').order_by('-date_joined')
    
    if request.method == 'POST':
        lecturer_id = request.POST.get('lecturer_id')
        action = request.POST.get('action')
        
        try:
            lecturer = User.objects.get(id=lecturer_id, user_type='lecturer')
            
            if action == 'approve':
                lecturer.is_approved = True
                lecturer.save()
                messages.success(request, f'Lecturer {lecturer.get_full_name()} approved.')
            elif action == 'suspend':
                lecturer.is_active = False
                lecturer.save()
                messages.warning(request, f'Lecturer {lecturer.get_full_name()} suspended.')
            elif action == 'activate':
                lecturer.is_active = True
                lecturer.save()
                messages.success(request, f'Lecturer {lecturer.get_full_name()} activated.')
            elif action == 'delete':
                lecturer.delete()
                messages.info(request, f'Lecturer account deleted.')
        
        except User.DoesNotExist:
            messages.error(request, 'Lecturer not found.')
    
    return render(request, 'accounts/manage_lecturers.html', {'lecturers': lecturers})