from django.urls import path
from . import views

urlpatterns = [
    path('keypad/', views.keypad_ws, name='keypad_ws'),
    path('logs/', views.logs, name='logs'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('update-user', views.update_user, name='update_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('login-view', views.login_view, name='login'),
    path('logout-view', views.logout_view, name='logout'),
]
