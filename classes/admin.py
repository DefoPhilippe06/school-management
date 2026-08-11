from django.contrib import admin
from .models import Level, ClassRoom, TimeSlot

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order',)

@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'school_year', 'capacity')
    list_filter = ('level', 'school_year')
    search_fields = ('name',)

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('classroom', 'day', 'start_time', 'end_time', 'subject', 'teacher', 'room')
    list_filter = ('day', 'classroom', 'subject')
    search_fields = ('classroom__name', 'subject__name')
    ordering = ('day', 'start_time')