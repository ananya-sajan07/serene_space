# View functions for Custom Admin Panel (adminapp)

# This module handles all the admin dashboard functionality including:
# - Admin authentication (login/logout)
# - User management
# - Doctor management  
# - Book management
# - Registration and login pages for users/doctors

# All admin routes are prefixed with /admin/
# Example: /admin/login/, /admin/dashboard/, /admin/manage_users/

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import SereneAdmin
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from core.models import User

@csrf_exempt
def admin_login(request):
    print("=== ADMIN LOGIN VIEW CALLED ===")
    print(f"Request method: {request.method}")
    print(f"Request path: {request.path}")
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(f"Email: {email}, Password: {password}")
        
        try:
            admin = SereneAdmin.objects.get(Email=email, password=password)
            print("Login SUCCESS")
            
            request.session['admin_id'] = admin.id
            request.session['admin_email'] = admin.Email
            request.session['admin_logged_in'] = True
            
            return redirect('admin_dashboard')
            
        except SereneAdmin.DoesNotExist:
            print("Login FAILED - Invalid credentials")
            return render(request, 'adminapp/admin_login.html', {
                'error': 'Invalid email or password'
            })
    
    print("Showing login form (GET request)")
    return render(request, 'adminapp/admin_login.html')
    
def admin_dashboard(request):
    #Check if admin is logged in
    if not request.session.get('admin_logged_in'):
        return redirect('admin_login')
    
    #Admin is logged in - Show Dashboard
    return render(request,'adminapp/admin_dashboard.html')
    
def admin_logout(request):
    #Clear Session
    request.session.flush()
    return redirect('admin_login')

def manage_users(request):
    #Check if admin is logged in
    if not request.session.get('admin_logged_in'):
        return redirect('admin_login')
    
    #Admin is logged in, show manage users page
    return render(request, 'adminapp/manage_users.html')

def manage_doctors(request):
    if 'admin_email' not in request.session:
        return redirect('admin_login')
    
    return render(request, 'adminapp/manage_doctors.html')

def manage_books(request):
    if not request.session.get('admin_logged_in'): #Check if admin is logged in
        return redirect('admin_login')
    
    from core.models import Book #Get all books from Database
    books = Book.objects.all()

    return render(request, 'adminapp/manage_books.html', {'books': books}) #Pass books to template

def view_book(request, book_id):
    if not request.session.get('admin_logged_in'):
        return redirect('admin_login')
    
    try:
        from core.models import Book
        book = Book.objects.get(id=book_id)
        return render(request, 'adminapp/view_book.html', {'book': book})
    except Book.DoesNotExist:
        return render(request, 'adminapp/view_book.html', {'error': 'Book not found'})
    
def view_bookings(request):
    # Check if admin is logged in
    if not request.session.get('admin_logged_in'):
        return redirect('admin_login')
    
    # Get all bookings from database
    from core.models import Booking
    bookings = Booking.objects.all().order_by('-created_at')
    
    return render(request, 'adminapp/view_bookings.html', {'bookings': bookings})


def user_auth_page(request):
    # Combined login/registration for users (testing only)
    return render(request, 'adminapp/pages - testing only, not for production/user_auth.html')

def user_dashboard(request):
    # Simple dashboard for users (testing only)
    return render(request, 'adminapp/pages - testing only, not for production/user_dashboard.html')

def doctor_dashboard(request):
    # Simple dashboard for doctors (testing only)
    return render(request, 'adminapp/pages - testing only, not for production/doctor_dashboard.html')

def doctor_auth_page(request):
    # Combined login/registration for doctors (testing only)
    return render(request, 'adminapp/pages - testing only, not for production/doctor_auth.html')



