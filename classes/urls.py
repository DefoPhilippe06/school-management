from django.urls import path
from . import views

urlpatterns = [
    path('emploi-du-temps/', views.timetable_view, name='timetable'),
    path('save/', views.class_save, name='class_save'),
    path('level/save/', views.level_save, name='level_save'),
    path('delete/<int:pk>/', views.class_delete, name='class_delete'),
    path('level/delete/<int:pk>/', views.level_delete, name='level_delete'),
    path('', views.class_list, name='class_list'),
    path('niveaux/', views.level_list, name='level_list'),
    path('timeslot/save/', views.timeslot_save, name='timeslot_save'),
    path('timeslot/delete/<int:pk>/', views.timeslot_delete, name='timeslot_delete'),
]