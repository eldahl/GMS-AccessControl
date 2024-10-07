from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader

from .models import UserWithAccess
from .models import LogEntry

def portal(request):
    template = loader.get_template('test.html')
    testVar = "Phillip Dupont"
    context = {
        'testVar': testVar,
    }
    return HttpResponse(template.render(context, request));

def addLog(request):

    return HttpResponse();

# View for managing users
def manage_users(request):
    if request.method == 'POST':
        print("Post")
        # Collect form data
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        chip_identifier = request.POST['chip_identifier']
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

def logs(request):
    template = loader.get_template('logs.html')

    # Fetch all log entries
    logs = LogEntry.objects.all().values()
    context = {
        'logs': logs,
    }

    return HttpResponse(template.render(context, request));

def keypad_ws(request):

    template = loader.get_template('keypad.html')
    context = {}
    return HttpResponse(template.render(context, request));
