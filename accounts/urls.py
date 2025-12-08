from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Admin only URLs for lecturer management
    path('create-lecturer/', views.create_lecturer_view, name='create_lecturer'),
    path('manage-lecturers/', views.manage_lecturers_view, name='manage_lecturers'),
]