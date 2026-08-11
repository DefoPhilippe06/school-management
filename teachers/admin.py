from django.contrib import admin
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'user', 'specialization', 'phone', 'hire_date')
    list_filter = ('specialization',)
    search_fields = ('matricule', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)
    filter_horizontal = ('classes',)   # pour assigner facilement les classes
