from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('ajouter/', views.student_create, name='student_create'),
    path('save/', views.student_save, name='student_save'),
    path('delete/<int:pk>/', views.student_delete, name='student_delete'),
    path('import/', views.student_import, name='student_import'),
]