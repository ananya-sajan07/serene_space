from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import SereneAdmin
from django.views.decorators.csrf import csrf_exempt

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
                          





