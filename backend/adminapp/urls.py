# URL Configuration for Admin Dashboard (Custom Admin Panel)
# Defines all web page URLs for the admin section at /admin/
# Example: /admin/login/, /admin/dashboard/, /admin/manage_users/, etc.


from django.urls import path
from . import views
from .views import *
urlpatterns=[
                path('login/', views.admin_login, name = 'admin_login'),
                path('dashboard/', views.admin_dashboard, name = 'admin_dashboard'),
                path('logout/', views.admin_logout, name = 'admin_logout'),
                path('manage_users/', views.manage_users, name = 'manage_users'), 
                path('manage_doctors/', views.manage_doctors, name = 'manage_doctors'),        
                path('manage_books/', views.manage_books, name = 'manage_books' ),
                path('view_book/<int:book_id>/', views.view_book, name='view_book'),
                path('view_bookings/', views.view_bookings, name='view_bookings'),
                path('user_auth/', views.user_auth_page, name='user_auth'),
                path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
                path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
                path('doctor_auth/', views.doctor_auth_page, name='doctor_auth'),
            ]