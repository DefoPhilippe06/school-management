from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import ClassRoom, Level, TimeSlot
from core.models import SchoolYear
from subjects.models import Subject


@login_required
def timetable_view(request):
    current_year = SchoolYear.objects.filter(is_current=True).first()
    classes = ClassRoom.objects.filter(school_year=current_year) if current_year else []

    selected_class = request.GET.get('class')
    timeslots = []
    if selected_class:
        timeslots = TimeSlot.objects.filter(classroom_id=selected_class).select_related('subject', 'teacher')

    # Organiser par jour
    days = ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI']
    timetable = {day: [] for day in days}
    for slot in timeslots:
        timetable[slot.day].append(slot)

    context = {
        'classes': classes,
        'selected_class': selected_class,
        'timetable': timetable,
        'days': days,
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