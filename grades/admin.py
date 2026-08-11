from django.contrib import admin
from .models import SequenceGrade

@admin.register(SequenceGrade)
class SequenceGradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'school_year', 'sequence', 'score', 'trimester', 'created_by')
    list_filter = ('school_year', 'sequence', 'subject', 'student__current_class')
    search_fields = (
        'student__matricule',
        'student__user__first_name',
        'student__user__last_name',
        'subject__name',
    )
    raw_id_fields = ('student', 'subject', 'school_year', 'created_by')
    list_editable = ('score',)
    ordering = ('-school_year', 'student', 'subject', 'sequence')