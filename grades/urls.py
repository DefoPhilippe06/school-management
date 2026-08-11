from django.urls import path
from . import views

urlpatterns = [
    path('', views.grade_entry, name='grade_entry'),
    path('save/', views.grade_save, name='grade_save'),
    path('eleve/<int:student_id>/', views.student_grades, name='student_grades'),
    path('bulletin/<int:student_id>/pdf/', views.generate_bulletin_pdf, name='bulletin_pdf'),
]