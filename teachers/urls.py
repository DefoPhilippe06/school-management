from django.urls import path
from . import views

urlpatterns = [
    path('', views.teacher_list, name='teacher_list'),
    path('save/', views.teacher_save, name='teacher_save'),
    path('delete/<int:pk>/', views.teacher_delete, name='teacher_delete'),
]