from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import Attendance
from students.models import Student
from subjects.models import Subject
from core.models import SchoolYear
from classes.models import ClassRoom
from datetime import date


@login_required
@role_required('ADMIN', 'TEACHER')
def attendance_entry(request):
    current_year = SchoolYear.objects.filter(is_current=True).first()

    if request.user.role == 'TEACHER':
        try:
            teacher = request.user.teacher_profile
            classes = teacher.classes.filter(school_year=current_year)
            subjects = teacher.subjects.all()
        except:
            classes = ClassRoom.objects.none()
            subjects = Subject.objects.none()
    else:
        classes = ClassRoom.objects.filter(school_year=current_year) if current_year else []
        subjects = Subject.objects.all()

    selected_class = request.GET.get('class')
    selected_subject = request.GET.get('subject')
    selected_date = request.GET.get('date', date.today().isoformat())

    students = []
    if selected_class:
        students = Student.objects.filter(current_class_id=selected_class).select_related('user')

    context = {
        'classes': classes,
        'subjects': subjects,
        'students': students,
        'selected_class': selected_class,
        'selected_subject': selected_subject,
        'selected_date': selected_date,
        'current_year': current_year,
    }
    return render(request, 'attendance/attendance_entry.html', context)


@login_required
@role_required('ADMIN', 'TEACHER')
def attendance_save(request):
    if request.method == 'POST':
        class_id = request.POST.get('class')
        subject_id = request.POST.get('subject')
        attendance_date = request.POST.get('date')
        year_id = request.POST.get('year')
        hours = request.POST.get('hours', 1)

        current_year = get_object_or_404(SchoolYear, id=year_id)
        subject = get_object_or_404(Subject, id=subject_id) if subject_id else None

        for key in request.POST:
            if key.startswith('absent_'):
                student_id = key.split('_')[1]
                status = request.POST.get(f'status_{student_id}', 'UNJUSTIFIED')
                student = get_object_or_404(Student, id=student_id)

                Attendance.objects.create(
                    student=student,
                    school_year=current_year,
                    subject=subject,
                    date=attendance_date,
                    hours=hours,
                    status=status,
                    recorded_by=request.user
                )
        from accounts.utils import notify_admins
        if request.user.role == 'TEACHER':
            notify_admins(
                f"📋 {request.user.get_full_name() or request.user.username} a enregistré des absences "
                f"({attendance_date}).",
                link='/attendance/',
                exclude_user=request.user,
            )
        messages.success(request, "Absences enregistrées avec succès.")
        return redirect(f"/attendance/?class={class_id}&subject={subject_id}&date={attendance_date}")

    return redirect('attendance_entry')

@login_required
@role_required('ADMIN', 'TEACHER')
def attendance_list(request):
    from django.db.models import Q

    current_year = SchoolYear.objects.filter(is_current=True).first()
    attendances = Attendance.objects.filter(school_year=current_year).select_related(
        'student__user', 'subject', 'recorded_by'
    ).order_by('-date')

    # Filtres
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    class_id = request.GET.get('class', '')

    if query:
        attendances = attendances.filter(
            Q(student__matricule__icontains=query) |
            Q(student__user__first_name__icontains=query) |
            Q(student__user__last_name__icontains=query)
        )
    if status:
        attendances = attendances.filter(status=status)
    if class_id:
        attendances = attendances.filter(student__current_class_id=class_id)

    classes = ClassRoom.objects.filter(school_year=current_year) if current_year else []

    context = {
        'attendances': attendances,
        'classes': classes,
        'query': query,
        'selected_status': status,
        'selected_class': class_id,
    }
    return render(request, 'attendance/attendance_list.html', context)


@login_required
@role_required('ADMIN', 'TEACHER')
def attendance_update_status(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['JUSTIFIED', 'UNJUSTIFIED']:
            attendance.status = new_status
            attendance.save()
            messages.success(request, "Statut mis à jour.")
    return redirect('attendance_list')