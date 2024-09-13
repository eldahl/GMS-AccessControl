from django.urls import path
from . import views

urlpatterns = [
    path('portal/', views.portal, name='portal'),
    path('logs/', views.logs, name='logs'),
    path('keypad/', views.keypad_ws, name='keypad_ws'),
]
