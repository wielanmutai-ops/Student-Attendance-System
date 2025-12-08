# from django.urls import path
# from . import views

# urlpatterns = [
#     # Lecturer URLs
#     path('lecturer/', views.lecturer_dashboard, name='lecturer_dashboard'),
#     path('create-session/', views.create_attendance_session, name='create_attendance_session'),
#     path('generate-code/<int:session_id>/', views.generate_attendance_code, name='generate_attendance_code'),
#     path('session/<int:session_id>/', views.view_session_attendance, name='view_session_attendance'),
#     path('session/<int:session_id>/pdf/', views.download_attendance_pdf, name='download_attendance_pdf'),
#     path('session/<int:session_id>/submit/', views.submit_attendance_report, name='submit_attendance_report'),
    
#     # Student URLs
#     path('student/', views.student_dashboard, name='student_dashboard'),
#     path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    
#     # Admin URLs
#     path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
#     path('admin/review-reports/', views.admin_review_reports, name='admin_review_reports'),
# ]


from django.urls import path
from . import views

urlpatterns = [
    # Lecturer URLs
    path('lecturer/', views.lecturer_dashboard, name='lecturer_dashboard'),
    path('create-session/', views.create_attendance_session, name='create_attendance_session'),
    path('generate-code/<int:session_id>/', views.generate_attendance_code, name='generate_attendance_code'),
    path('session/<int:session_id>/', views.view_session_attendance, name='view_session_attendance'),
    path('session/<int:session_id>/pdf/', views.download_attendance_pdf, name='download_attendance_pdf'),
    path('session/<int:session_id>/submit/', views.submit_attendance_report, name='submit_attendance_report'),
    
    # Student URLs
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/review-reports/', views.admin_review_reports, name='admin_review_reports'),
    path('admin/levels/', views.manage_levels, name='manage_levels'),
    path('admin/levels/create/', views.create_level, name='create_level'),
    path('admin/levels/edit/<int:level_id>/', views.edit_level, name='edit_level'),
    path('admin/courses/', views.manage_courses, name='manage_courses'),
    path('admin/courses/create/', views.create_course, name='create_course'),
    path('admin/courses/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('admin/units/', views.manage_units, name='manage_units'),
    path('admin/units/create/', views.create_unit, name='create_unit'),
    path('admin/units/edit/<int:unit_id>/', views.edit_unit, name='edit_unit'),
    path('admin/assign-units/', views.assign_units, name='assign_units'),
    path('admin/units/create/', views.create_unit, name='create_unit'),
    path('units/delete/<int:unit_id>/', views.delete_unit, name='delete_unit'), 
  ]