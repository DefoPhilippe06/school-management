from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'hours', 'status', 'subject', 'sequence', 'school_year', 'recorded_by')
    list_filter = ('status', 'school_year', 'sequence', 'subject')
    search_fields = (
        'student__matricule',
        'student__user__first_name',
        'student__user__last_name',
    )
    raw_id_fields = ('student', 'school_year', 'subject', 'recorded_by')
    date_hierarchy = 'date'