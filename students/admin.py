from django.contrib import admin
from .models import Student, Parent, Enrollment

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'user', 'current_class', 'gender', 'date_of_birth')
    list_filter = ('gender', 'current_class', 'current_class__school_year')
    search_fields = ('matricule', 'user__first_name', 'user__last_name', 'user__username')
    raw_id_fields = ('user', 'current_class')

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'profession')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'phone')
    filter_horizontal = ('students',)
    raw_id_fields = ('user',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'classroom', 'school_year', 'status', 'enrollment_date')
    list_filter = ('status', 'school_year', 'classroom__level')
    search_fields = ('student__matricule', 'student__user__first_name', 'student__user__last_name')
    raw_id_fields = ('student', 'classroom', 'school_year')
