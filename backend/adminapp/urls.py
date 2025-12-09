from django.urls import path
from . import views
from .views import *
urlpatterns=[
                path('login/', views.admin_login, name = 'admin_login'),
                path('dashboard/', views.admin_dashboard, name = 'admin_dashboard'),
                path('logout/', views.admin_logout, name = 'admin_logout'),
                path('manage_users/', views.manage_users, name = 'manage_users'), 
                path('manage_doctors/', views.manage_doctors, name = 'manage_doctors'),
                path('doctor_registration_page/', views.doctor_registration_page, name = 'doctor_registration_page'),
                path('user_registration_page/', views.user_registration_page, name = 'user_registration_page'),
                path('user_login_page/', views.user_login_page, name = 'user_login_page'),
                path('user_edit_page/', views.user_edit_page, name ='user_edit_page'),
                path('doctor_login_page/', views.doctor_login_page, name = 'doctor_login_page'),
                path('doctor_edit_page/', views.doctor_edit_page, name = 'doctor_edit_page'),
            ]