from django.urls import path
from . import views

urlpatterns = [
    path('portal/', views.portal, name='portal'),
    path('logs/', views.logs, name='logs'),
    path('keypad/', views.keypad_ws, name='keypad_ws'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
]
