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
                          

def doctor_registration_page(request):
    # Simple Page for Doctors to Register (not Admin Protected)
    return render(request, 'adminapp/doctor_register.html')


def user_registration_page(request):
    #Simple Page for Users to Register (not Admin Protected)
    return render(request, 'adminapp/user_register.html')

def user_login_page(request):
    #Simple Page for Users to Login (not Admin Protected)
    return render(request, 'adminapp/user_login.html')

def user_edit_page(request):
    #Simple Page for Users to Edit their Details (not Admin Protected)
    return render(request, 'adminapp/user_edit.html')

def doctor_login_page(request):
    #Simple Page for Doctors to Login (not Admin Protected)
    return render(request, 'adminapp/doctor_login.html')

def doctor_edit_page(request):
    #Simple Page for Doctors to Edit their Details (not Admin Protected)
    return render(request, 'adminapp/doctor_edit.html')