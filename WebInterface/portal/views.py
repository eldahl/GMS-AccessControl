from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

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

    logs = [
        {
            'timestamp': "10-10-2021",
            'level': 1,
            'message': "test",
        },
        {
            'timestamp': "10-10-2021",
            'level': 1,
            'message': "test",
        },
        {
            'timestamp': "10-10-2021",
            'level': 1,
            'message': "test",
        },
        {
            'timestamp': "10-10-2021",
            'level': 1,
            'message': "test",
        },
    ]
    context = {
        'logs': logs,
    }

    return HttpResponse(template.render(context, request));

def keypad_ws(request):

    template = loader.get_template('keypad.html')
    context = {}
    return HttpResponse(template.render(context, request));
