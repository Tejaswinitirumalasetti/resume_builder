from django.urls import path
from . import views

urlpatterns = [
    path('', views.register, name='home'),  # ADD THIS

    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_resume, name='create_resume'),
    path('export/<int:resume_id>/', views.export_pdf, name='export_pdf'),
]