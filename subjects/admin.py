from django.contrib import admin
from .models import Subject

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'coefficient')
    list_filter = ('levels',)
    search_fields = ('name', 'code')
    filter_horizontal = ('levels', 'teachers')