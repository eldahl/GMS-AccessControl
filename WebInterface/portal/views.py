from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

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
