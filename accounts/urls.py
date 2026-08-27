from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('parent/', views.parent_dashboard, name='parent_dashboard'),
    path('enseignant/', views.teacher_dashboard, name='teacher_dashboard'),
    path('notification/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('admins/', views.admin_list, name='admin_list'),
    path('admins/save/', views.admin_save, name='admin_save'),
    path('admins/delete/<int:pk>/', views.admin_delete, name='admin_delete'),
    path('profil/', views.profile_edit, name='profile_edit'),
]