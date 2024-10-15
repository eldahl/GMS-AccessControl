from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session

from .models import UserWithAccess
from .models import LogEntry

def portal(request):
    template = loader.get_template('test.html')
    testVar = "Phillip Dupont"
    context = {
        'testVar': testVar,
    }
    return HttpResponse(template.render(context, request));

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # set user-specific data in the session
            request.session['username'] = username
            request.session.save()
            return redirect('manage_users')
        else:
            # Handle invalid login
            return render(request, 'login.html', { 'error': 'Invalid login.' })
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    # Clear the user's session data
    Session.objects.filter(session_key=request.session.session_key).delete()
    return redirect('login')

def checkForAuth(request):
    if request.user.is_authenticated:
        return True
    else:
        return False

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

        # Create new user with form data
        new_user = UserWithAccess(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            chip_identifier=chip_identifier.encode(),  # Encode binary field
            pass_code=pass_code
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
        
        # Get user
        user = UserWithAccess.objects.filter(id=user_id).get()
        
        # Update fields
        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.chip_identifier = chip_identifier
        user.pass_code = pass_code
        
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
