import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io

from accounts.models import User, StudentProfile, LecturerProfile
from .models import Level, Course, Unit, AttendanceSession, AttendanceRecord, AttendanceReport
from .forms import LevelForm, CourseForm, UnitForm, UnitAssignmentForm, AttendanceSessionForm, AttendanceCodeForm, AttendanceReportForm
from accounts.views import admin_required


@login_required
def lecturer_dashboard(request):
    if request.user.user_type != 'lecturer':
        return redirect('student_dashboard')
    
    # Get or create lecturer profile
    try:
        lecturer = request.user.lecturer_profile
    except LecturerProfile.DoesNotExist:
        lecturer = LecturerProfile.objects.create(
            user=request.user,
            qualification="",
            specialization=""
        )
        messages.info(request, 'Lecturer profile created successfully.')
    
    today = timezone.now().date()
    
    # Get today's sessions
    today_sessions = AttendanceSession.objects.filter(
        lecturer=lecturer,
        session_date=today
    ).order_by('-start_time')
    
    # Get upcoming sessions (next 7 days)
    upcoming_sessions = AttendanceSession.objects.filter(
        lecturer=lecturer,
        session_date__gt=today,
        session_date__lte=today + timezone.timedelta(days=7)
    ).order_by('session_date', 'start_time')
    
    # Get assigned units - CHANGED: lecturer → lecturers (ManyToManyField)
    assigned_units = Unit.objects.filter(lecturers=lecturer).select_related('course', 'academic_level')
    
    context = {
        'today_sessions': today_sessions,
        'upcoming_sessions': upcoming_sessions,
        'assigned_units': assigned_units,
        'total_sessions': AttendanceSession.objects.filter(lecturer=lecturer).count(),
    }
    
    return render(request, 'attendance/lecturer_dashboard.html', context)

@login_required
def student_dashboard(request):
    if request.user.user_type != 'student':
        return redirect('lecturer_dashboard')
    
    # Get or create student profile
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        student = StudentProfile.objects.create(
            user=request.user,
            enrollment_date=timezone.now().date()
        )
        messages.info(request, 'Student profile created successfully.')
    
    today = timezone.now().date()
    
    # Get today's attendance records
    today_attendance = AttendanceRecord.objects.filter(
        student=student,
        session__session_date=today
    ).select_related('session', 'session__unit')
    
    # Get overall attendance statistics
    total_sessions = AttendanceSession.objects.filter(
        unit__students=student
    ).count()
    
    attended_sessions = AttendanceRecord.objects.filter(
        student=student
    ).count()
    
    attendance_percentage = (attended_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    # Get enrolled units
    units = student.enrolled_units.all()
    
    context = {
        'today_attendance': today_attendance,
        'attendance_percentage': round(attendance_percentage, 2),
        'total_sessions': total_sessions,
        'attended_sessions': attended_sessions,
        'units': units,
    }
    
    return render(request, 'attendance/student_dashboard.html', context)

@login_required
def admin_dashboard(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    # Get statistics
    total_students = User.objects.filter(user_type='student').count()
    total_lecturers = User.objects.filter(user_type='lecturer').count()
    pending_lecturers = User.objects.filter(user_type='lecturer', is_approved=False).count()
    total_courses = Course.objects.count()
    total_units = Unit.objects.count()
    
    context = {
        'total_students': total_students,
        'total_lecturers': total_lecturers,
        'pending_lecturers': pending_lecturers,
        'total_courses': total_courses,
        'total_units': total_units,
    }
    
    return render(request, 'attendance/admin_dashboard.html', context)

@login_required
def create_attendance_session(request):
    if request.user.user_type != 'lecturer':
        return redirect('dashboard')
    
    lecturer = request.user.lecturer_profile
    
    if request.method == 'POST':
        form = AttendanceSessionForm(lecturer, request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.lecturer = lecturer
            session.save()
            
            # Generate attendance code
            code = session.generate_attendance_code()
            
            messages.success(request, f'Attendance session created! Code: {code}')
            return redirect('lecturer_dashboard')
    else:
        form = AttendanceSessionForm(lecturer)
    
    return render(request, 'attendance/create_session.html', {'form': form})

@login_required
def generate_attendance_code(request, session_id):
    if request.user.user_type != 'lecturer':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    session = get_object_or_404(AttendanceSession, id=session_id, lecturer=request.user.lecturer_profile)
    
    if session.is_code_valid():
        return JsonResponse({
            'error': 'Code is still valid',
            'code': session.attendance_code,
            'expires_at': session.code_expires_at.strftime('%H:%M:%S')
        })
    
    code = session.generate_attendance_code()
    
    return JsonResponse({
        'code': code,
        'expires_at': session.code_expires_at.strftime('%H:%M:%S'),
        'message': 'New code generated successfully'
    })

@login_required
def mark_attendance(request):
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can mark attendance')
        return redirect('dashboard')
    
    # Get or create student profile
    try:
        student = request.user.student_profile
    except StudentProfile.DoesNotExist:
        student = StudentProfile.objects.create(
            user=request.user,
            enrollment_date=timezone.now().date()
        )
        messages.info(request, 'Student profile created.')
    
    if request.method == 'POST':
        form = AttendanceCodeForm(request.POST)
        if form.is_valid():
            messages.info(request, 'Attendance marking functionality will be implemented soon.')
            return redirect('student_dashboard')
    else:
        form = AttendanceCodeForm()
    
    return render(request, 'attendance/mark_attendance.html', {'form': form})

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def view_session_attendance(request, session_id):
    if request.user.user_type != 'lecturer':
        return redirect('dashboard')
    
    session = get_object_or_404(
        AttendanceSession, 
        id=session_id, 
        lecturer=request.user.lecturer_profile
    )
    
    # Get present and absent students
    present_students = StudentProfile.objects.filter(
        attendance_records__session=session
    ).distinct()
    
    absent_students = session.unit.students.exclude(
        id__in=present_students.values_list('id', flat=True)
    )
    
    # Get or create attendance report
    report, created = AttendanceReport.objects.get_or_create(
        session=session,
        defaults={'submitted_by': request.user.lecturer_profile}
    )
    
    context = {
        'session': session,
        'present_students': present_students,
        'absent_students': absent_students,
        'total_students': session.unit.students.count(),
        'present_count': present_students.count(),
        'absent_count': absent_students.count(),
        'report': report,
    }
    
    return render(request, 'attendance/session_attendance.html', context)

@login_required
def download_attendance_pdf(request, session_id):
    if request.user.user_type != 'lecturer':
        return redirect('dashboard')
    
    session = get_object_or_404(
        AttendanceSession,
        id=session_id,
        lecturer=request.user.lecturer_profile
    )
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Add title
    title = Paragraph(f"Attendance Report - {session.unit.name}", styles['Title'])
    elements.append(title)
    
    # Add session details
    details = [
        ['Date:', str(session.session_date)],
        ['Time:', f"{session.start_time} - {session.end_time}"],
        ['Location:', session.location],
        ['Unit Code:', session.unit.code],
        ['Lecturer:', session.lecturer.user.get_full_name()],
    ]
    
    details_table = Table(details)
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
    ]))
    elements.append(details_table)
    
    # Add present students
    elements.append(Paragraph("<br/><br/>Present Students:", styles['Heading2']))
    
    present_students = StudentProfile.objects.filter(
        attendance_records__session=session
    ).distinct()
    
    present_data = [['Registration Number', 'Name', 'Time Marked']]
    for student in present_students:
        record = AttendanceRecord.objects.get(student=student, session=session)
        present_data.append([
            student.user.registration_number,
            student.user.get_full_name(),
            record.marked_at.strftime('%H:%M:%S')
        ])
    
    present_table = Table(present_data)
    present_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(present_table)
    
    # Add statistics
    total_students = session.unit.students.count()
    present_count = present_students.count()
    absent_count = total_students - present_count
    
    elements.append(Paragraph("<br/><br/>Statistics:", styles['Heading2']))
    stats_data = [
        ['Total Students:', str(total_students)],
        ['Present:', str(present_count)],
        ['Absent:', str(absent_count)],
        ['Attendance Rate:', f"{(present_count/total_students*100):.1f}%"],
    ]
    
    stats_table = Table(stats_data)
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
    ]))
    elements.append(stats_table)
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF value from buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="attendance_{session_id}.pdf"'
    response.write(pdf)
    
    return response

@login_required
def submit_attendance_report(request, session_id):
    if request.user.user_type != 'lecturer':
        return redirect('dashboard')
    
    session = get_object_or_404(
        AttendanceSession,
        id=session_id,
        lecturer=request.user.lecturer_profile
    )
    
    report, created = AttendanceReport.objects.get_or_create(
        session=session,
        defaults={'submitted_by': request.user.lecturer_profile}
    )
    
    if request.method == 'POST':
        report.status = 'submitted'
        report.save()
        
        messages.success(request, 'Attendance report submitted to admin')
        return redirect('view_session_attendance', session_id=session_id)
    
    return redirect('view_session_attendance', session_id=session_id)

@login_required
def admin_review_reports(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    reports = AttendanceReport.objects.filter(status='submitted').order_by('-submitted_at')
    
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        report = get_object_or_404(AttendanceReport, id=report_id)
        
        if action == 'approve':
            report.status = 'reviewed'
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.admin_notes = notes
            report.save()
            messages.success(request, 'Report approved successfully')
        elif action == 'reject':
            report.status = 'rejected'
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.admin_notes = notes
            report.save()
            messages.warning(request, 'Report rejected')
    
    return render(request, 'attendance/admin_review.html', {'reports': reports})

# ==================== NEW COURSE MANAGEMENT VIEWS ====================

@login_required
@admin_required
def manage_levels(request):
    """Admin manages academic levels"""
    levels = Level.objects.all().order_by('year', 'semester')
    
    if request.method == 'POST':
        if 'delete' in request.POST:
            level_id = request.POST.get('level_id')
            try:
                level = Level.objects.get(id=level_id)
                level.delete()
                messages.success(request, f'Level "{level.name}" deleted successfully.')
            except Level.DoesNotExist:
                messages.error(request, 'Level not found.')
        
        elif 'edit' in request.POST:
            level_id = request.POST.get('level_id')
            return redirect('edit_level', level_id=level_id)
    
    return render(request, 'attendance/manage_levels.html', {'levels': levels})

@login_required
@admin_required
def create_level(request):
    """Admin creates new academic level"""
    if request.method == 'POST':
        form = LevelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Level created successfully.')
            return redirect('manage_levels')
    else:
        form = LevelForm()
    
    return render(request, 'attendance/create_level.html', {'form': form})

@login_required
@admin_required
def edit_level(request, level_id):
    """Admin edits academic level"""
    level = get_object_or_404(Level, id=level_id)
    
    if request.method == 'POST':
        form = LevelForm(request.POST, instance=level)
        if form.is_valid():
            form.save()
            messages.success(request, 'Level updated successfully.')
            return redirect('manage_levels')
    else:
        form = LevelForm(instance=level)
    
    return render(request, 'attendance/edit_level.html', {'form': form, 'level': level})

@login_required
@admin_required
def manage_courses(request):
    """Admin manages courses"""
    courses = Course.objects.all().select_related('level').order_by('level', 'name')
    
    if request.method == 'POST':
        if 'delete' in request.POST:
            course_id = request.POST.get('course_id')
            try:
                course = Course.objects.get(id=course_id)
                course.delete()
                messages.success(request, f'Course "{course.name}" deleted successfully.')
            except Course.DoesNotExist:
                messages.error(request, 'Course not found.')
        
        elif 'edit' in request.POST:
            course_id = request.POST.get('course_id')
            return redirect('edit_course', course_id=course_id)
    
    return render(request, 'attendance/manage_courses.html', {'courses': courses})

@login_required
@admin_required
def create_course(request):
    """Admin creates new course"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course created successfully.')
            return redirect('manage_courses')
    else:
        form = CourseForm()

        levels = Level.objects.all().order_by('year', 'semester')
    
    return render(request, 'attendance/create_course.html', {
        'form': form,
        'levels': levels 
    })
   
    return render(request, 'attendance/create_course.html', {'form': form})

@login_required
@admin_required
def edit_course(request, course_id):
    """Admin edits course"""
    course = get_object_or_404(Course, id=course_id)
    levels = Level.objects.all().order_by('year', 'semester')
    
    if request.method == 'POST':
        # Update fields manually
        course.name = request.POST.get('name')
        course.code = request.POST.get('code')
        course.level_id = request.POST.get('level')
        
        # FIX: Make sure duration_years is not empty
        duration_years = request.POST.get('duration_years')
        if duration_years:  # Check if it's not empty
            course.duration_years = int(duration_years)
        else:
            course.duration_years = 3  # Default value
        
        course.is_active = request.POST.get('is_active') == 'on'
        course.save()
        
        messages.success(request, 'Course updated successfully.')
        return redirect('manage_courses')
    
    return render(request, 'attendance/edit_course.html', {
        'course': course,
        'levels': levels
    })

# @login_required
# @admin_required
# def manage_units(request):
#     """Admin manages units"""
#     units = Unit.objects.all().select_related('course', 'lecturer').order_by('course', 'semester', 'code')
    
#     if request.method == 'POST':
#         if 'delete' in request.POST:
#             unit_id = request.POST.get('unit_id')
#             try:
#                 unit = Unit.objects.get(id=unit_id)
#                 unit.delete()
#                 messages.success(request, f'Unit "{unit.name}" deleted successfully.')
#             except Unit.DoesNotExist:
#                 messages.error(request, 'Unit not found.')
        
#         elif 'edit' in request.POST:
#             unit_id = request.POST.get('unit_id')
#             return redirect('edit_unit', unit_id=unit_id)
    
#     return render(request, 'attendance/manage_units.html', {'units': units})

@login_required
@admin_required
def manage_units(request):
    """Admin manages units"""
    # CORRECTED: select_related('course', 'academic_level').prefetch_related('lecturers')
    units = Unit.objects.all().select_related('course', 'academic_level').prefetch_related('lecturers').order_by('course', 'academic_level__year', 'academic_level__semester', 'code')
    
    if request.method == 'POST':
        if 'delete' in request.POST:
            unit_id = request.POST.get('unit_id')
            try:
                unit = Unit.objects.get(id=unit_id)
                unit_name = unit.name
                unit.delete()
                messages.success(request, f'Unit "{unit_name}" deleted successfully.')
            except Unit.DoesNotExist:
                messages.error(request, 'Unit not found.')
        
        elif 'edit' in request.POST:
            unit_id = request.POST.get('unit_id')
            return redirect('edit_unit', unit_id=unit_id)
    
    return render(request, 'attendance/manage_units.html', {'units': units})

@login_required
@admin_required
def create_unit(request):
    """Admin creates new unit"""
    from .models import Course, Unit, Level  # CHANGED: AcademicLevel → Level
    from django import forms
    
    # Create the form
    class UnitForm(forms.ModelForm):
        class Meta:
            model = Unit
            fields = ['code', 'name', 'course', 'academic_level', 'academic_year', 'is_core', 'description']
            widgets = {
                'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CS101'}),
                'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Introduction to Programming'}),
                'course': forms.Select(attrs={'class': 'form-select'}),
                'academic_level': forms.Select(attrs={'class': 'form-select'}),
                'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2024/2025'}),
                'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Unit description...'}),
            }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Populate academic_level choices with active Level objects
            self.fields['academic_level'].queryset = Level.objects.filter(is_active=True).order_by('year', 'semester')
            self.fields['course'].queryset = Course.objects.filter(is_active=True).order_by('code')
    
    if request.method == 'POST':
        form = UnitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Unit created successfully.')
            return redirect('manage_units')
        else:
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UnitForm()
    
    # Get levels for the template (optional)
    levels = Level.objects.filter(is_active=True).order_by('year', 'semester')
    
    return render(request, 'attendance/create_unit.html', {
        'form': form,
        'levels': levels,  # Pass levels to template if needed
    })

@login_required
@admin_required
def delete_unit(request, unit_id):
    """Delete a unit"""
    try:
        unit = Unit.objects.get(id=unit_id)
        unit_name = unit.name
        unit.delete()
        messages.success(request, f'Unit "{unit_name}" deleted successfully.')
    except Unit.DoesNotExist:
        messages.error(request, 'Unit not found.')
    except Exception as e:
        messages.error(request, f'Error deleting unit: {str(e)}')
    
    return redirect('manage_units')

@login_required
@admin_required
def edit_unit(request, unit_id):
    """Admin edits unit"""
    unit = get_object_or_404(Unit, id=unit_id)
    
    if request.method == 'POST':
        form = UnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request, 'Unit updated successfully.')
            return redirect('manage_units')
    else:
        form = UnitForm(instance=unit)
    
    return render(request, 'attendance/edit_unit.html', {'form': form, 'unit': unit})

# @login_required
# @admin_required
# def assign_units(request):
#     """Admin assigns units to lecturers"""
#     if request.method == 'POST':
#         form = UnitAssignmentForm(request.POST)
#         if form.is_valid():
#             lecturer = form.cleaned_data['lecturer']
#             units = form.cleaned_data['units']
            
#             # Assign units to lecturer
#             units.update(lecturer=lecturer)
            
#             messages.success(request, f'{units.count()} units assigned to {lecturer.user.get_full_name()}.')
#             return redirect('assign_units')
#     else:
#         form = UnitAssignmentForm()
    
#     return render(request, 'attendance/assign_units.html', {'form': form})
@login_required
@admin_required
def assign_units(request):
    """Admin assigns units to multiple lecturers"""
    if request.method == 'POST':
        form = UnitAssignmentForm(request.POST)
        if form.is_valid():
            # CHANGED: 'lecturer' → 'lecturers'
            lecturers = form.cleaned_data['lecturers']  # Plural!
            units = form.cleaned_data['units']
            
            # Assign each unit to each lecturer (Many-to-Many)
            for unit in units:
                unit.lecturers.add(*lecturers)  # Add all selected lecturers
            
            lecturer_names = ', '.join([l.user.get_full_name() for l in lecturers])
            messages.success(request, f'{units.count()} units assigned to {lecturer_names}.')
            return redirect('assign_units')
    else:
        form = UnitAssignmentForm()
    
    return render(request, 'attendance/assign_units.html', {'form': form})