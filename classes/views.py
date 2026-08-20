from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import ClassRoom, Level, TimeSlot
from core.models import SchoolYear
from subjects.models import Subject
from django.urls import reverse


@login_required
def timetable_view(request):
    current_year = SchoolYear.objects.filter(is_current=True).first()
    classes = ClassRoom.objects.filter(school_year=current_year) if current_year else []

    selected_class = request.GET.get('class')
    timeslots = []
    if selected_class:
        timeslots = TimeSlot.objects.filter(classroom_id=selected_class).select_related(
            'subject', 'teacher', 'teacher__user'
        )

    days = ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI']
    timetable = {day: [] for day in days}
    for slot in timeslots:
        timetable[slot.day].append(slot)

    context = {
        'classes': classes,
        'selected_class': selected_class,
        'timetable': timetable,
        'days': days,
        'subjects': Subject.objects.all(),
        'teachers': Teacher.objects.select_related('user').all(),
        'is_admin': request.user.role == 'ADMIN' or request.user.is_superuser,
    }
    return render(request, 'classes/timetable.html', context)

from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from django.contrib import messages
from .models import ClassRoom, Level
from core.models import SchoolYear


@login_required
@role_required('ADMIN')
def class_save(request):
    if request.method == 'POST':
        class_id = request.POST.get('class_id')
        name = request.POST.get('name').strip()
        level_id = request.POST.get('level')
        capacity = request.POST.get('capacity', 50)

        current_year = SchoolYear.objects.filter(is_current=True).first()
        level = Level.objects.get(id=level_id)

        if class_id:
            # Modification
            classroom = ClassRoom.objects.get(id=class_id)
            classroom.name = name
            classroom.level = level
            classroom.capacity = capacity
            classroom.save()
            messages.success(request, f"Classe « {name} » modifiée avec succès.")
        else:
            # Création
            if ClassRoom.objects.filter(name=name, school_year=current_year).exists():
                messages.error(request, f"La classe « {name} » existe déjà pour cette année scolaire.")
            else:
                ClassRoom.objects.create(
                    name=name,
                    level=level,
                    school_year=current_year,
                    capacity=capacity
                )
                messages.success(request, f"Classe « {name} » créée avec succès.")

    return redirect('dashboard')

@login_required
@role_required('ADMIN')
def level_save(request):
    if request.method == 'POST':
        level_id = request.POST.get('level_id')
        name = request.POST.get('name').strip()
        order = request.POST.get('order', 0)

        if level_id:
            level = Level.objects.get(id=level_id)
            level.name = name
            level.order = order
            level.save()
            messages.success(request, f"Niveau « {name} » modifié.")
        else:
            if Level.objects.filter(name=name).exists():
                messages.error(request, f"Le niveau « {name} » existe déjà.")
            else:
                Level.objects.create(name=name, order=order)
                messages.success(request, f"Niveau « {name} » créé.")

    return redirect('dashboard')

@login_required
@role_required('ADMIN')
def class_delete(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    name = classroom.name
    classroom.delete()
    messages.success(request, f"Classe « {name} » supprimée.")
    return redirect('dashboard')


@login_required
@role_required('ADMIN')
def level_delete(request, pk):
    level = get_object_or_404(Level, pk=pk)
    name = level.name
    level.delete()
    messages.success(request, f"Niveau « {name} » supprimé.")
    return redirect('dashboard')

@login_required
@role_required('ADMIN')
def class_list(request):
    current_year = SchoolYear.objects.filter(is_current=True).first()
    classes = ClassRoom.objects.filter(school_year=current_year).select_related('level') if current_year else []
    levels = Level.objects.all()
    return render(request, 'classes/class_list.html', {
        'classes': classes,
        'levels': levels,
        'current_year': current_year
    })

@login_required
@role_required('ADMIN')
def level_list(request):
    levels = Level.objects.all().order_by('order')
    return render(request, 'classes/level_list.html', {'levels': levels})

from teachers.models import Teacher


@login_required
@role_required('ADMIN')
def timeslot_save(request):
    if request.method == 'POST':
        slot_id = request.POST.get('slot_id')
        classroom_id = request.POST.get('classroom')
        subject_id = request.POST.get('subject')
        teacher_id = request.POST.get('teacher') or None
        day = request.POST.get('day')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        room = request.POST.get('room', '').strip()

        if slot_id:
            slot = get_object_or_404(TimeSlot, id=slot_id)
            slot.classroom_id = classroom_id
            slot.subject_id = subject_id
            slot.teacher_id = teacher_id
            slot.day = day
            slot.start_time = start_time
            slot.end_time = end_time
            slot.room = room
            slot.save()
            messages.success(request, "Créneau modifié.")
        else:
            TimeSlot.objects.create(
                classroom_id=classroom_id,
                subject_id=subject_id,
                teacher_id=teacher_id,
                day=day,
                start_time=start_time,
                end_time=end_time,
                room=room,
            )
            messages.success(request, "Créneau ajouté.")

    selected = request.POST.get('classroom') or request.GET.get('class', '')
    return redirect(f"{reverse('timetable')}?class={selected}" if selected else 'timetable')


@login_required
@role_required('ADMIN')
def timeslot_delete(request, pk):
    slot = get_object_or_404(TimeSlot, pk=pk)
    classroom_id = slot.classroom_id
    slot.delete()
    messages.success(request, "Créneau supprimé.")
    return redirect(f"{reverse('timetable')}?class={classroom_id}")