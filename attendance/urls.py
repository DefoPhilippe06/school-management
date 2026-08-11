from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_entry, name='attendance_entry'),
    path('liste/', views.attendance_list, name='attendance_list'),
    path('save/', views.attendance_save, name='attendance_save'),
    path('status/<int:pk>/', views.attendance_update_status, name='attendance_update_status'),
]