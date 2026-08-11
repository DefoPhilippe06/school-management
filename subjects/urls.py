from django.urls import path
from . import views

urlpatterns = [
    path('', views.subject_list, name='subject_list'),
    path('save/', views.subject_save, name='subject_save'),
    path('delete/<int:pk>/', views.subject_delete, name='subject_delete'),
]