from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session

from .models import UserWithAccess
from .models import LogEntry

def root_redirect(request):
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Try Django superuser authentication first
        from django.contrib.auth import authenticate, login as auth_login
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            auth_login(request, user)
            loginEntry = LogEntry(event="Admin Event", message=f"Superuser logged in! User: {user.username}")
            loginEntry.save()
            request.session['username'] = username
            request.session['user_id'] = user.id
            request.session['is_superuser'] = True
            request.session.save()
            return redirect('manage_users')
        # Fallback to UserWithAccess authentication
        try:
            user = UserWithAccess.objects.get(username=username)
            if user.pass_code == password:
                loginEntry = LogEntry(event="Admin Event", message=f"Admin logged in! User: {user.username}")
                loginEntry.save()
                request.session['username'] = username
                request.session['user_id'] = user.id
                request.session['is_superuser'] = False
                request.session.save()
                return redirect('manage_users')
            else:
                return render(request, 'login.html', { 'error': 'Invalid login.' })
        except UserWithAccess.DoesNotExist:
            return render(request, 'login.html', { 'error': 'Invalid login.' })
    return render(request, 'login.html')

def logout_view(request):
    # Add login to logs
    username = request.session.get('username', 'Unknown')
    loginEntry = LogEntry(event="Admin Event", message=f"Admin logged out! User: {username}")
    loginEntry.save()
    # Clear the user's session data
    request.session.flush()
    return redirect('login')

def checkForAuth(request):
    return 'username' in request.session

# View for managing users
def manage_users(request):
    if checkForAuth(request) is not True:
        return redirect('login')

    if request.method == 'POST':
        # Collect form data
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        chip_identifier = request.POST['chip_identifier']
        # Remove binary notation and encode
        if chip_identifier.startswith('b'):
            chip_identifier = chip_identifier[2:-1].encode()
        pass_code = request.POST['pass_code']
        username = request.POST['username']

        # Create new user with form data
        new_user = UserWithAccess(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            chip_identifier=chip_identifier.encode(),  # Encode binary field
            pass_code=pass_code,
            username=username
        )
        new_user.save()

        return redirect('manage_users')

    # Fetch all users for displaying in the template
    users = UserWithAccess.objects.all()

    return render(request, 'manage_users.html', {'users': users})

def update_user(request):
    if checkForAuth(request) is not True:
        return redirect('login')
    
    if request.method == 'GET':
        # Collect form data
        user_id = request.GET.get('user_id')
        first_name = request.GET.get('first_name')
        last_name = request.GET.get('last_name')
        phone = request.GET.get('phone')
        chip_identifier = request.GET.get('chip_identifier')
        # Remove binary notation and encode
        if chip_identifier.startswith('b'):
            chip_identifier = chip_identifier[2:-1].encode()
        pass_code = request.GET.get('pass_code')
        username = request.GET.get('username')
        
        # Get user
        user = UserWithAccess.objects.filter(id=user_id).get()
        
        # Update fields
        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.chip_identifier = chip_identifier
        user.pass_code = pass_code
        user.username = username
        
        # Save
        user.save()

    return redirect('manage_users')

def delete_user(request, user_id):
    if checkForAuth(request) is not True:
        return redirect('login')
    
    UserWithAccess.objects.filter(id=user_id).delete()

    return render(request, 'deleted_user.html')

def logs(request):
    template = loader.get_template('logs.html')

    # Fetch all log entries
    logs = LogEntry.objects.order_by('-timestamp')[:1000].values()
    context = {
        'logs': logs,
    }

    return HttpResponse(template.render(context, request));

def keypad_ws(request):

    template = loader.get_template('keypad.html')
    context = {}
    return HttpResponse(template.render(context, request));

def open_lock(request):
    if not checkForAuth(request):
        return redirect('login')
    # Import Coordinator and open the lock
    from . import hardwareHandler
    if hasattr(hardwareHandler, 'apps') and hasattr(hardwareHandler.apps, 'coordinator'):
        coordinator = hardwareHandler.apps.coordinator
        if hasattr(coordinator, 'serialCon'):
            coordinator.serialCon.write(b"o\n")
            LogEntry.objects.create(event="Manual Unlock", message=f"Lock opened by {request.session.get('username', 'Unknown')}")
            return HttpResponse("Lock opened!")
    # Fallback: just log the event
    LogEntry.objects.create(event="Manual Unlock", message=f"Lock open attempted by {request.session.get('username', 'Unknown')}")
    return HttpResponse("Lock open attempted (hardware not available)")
