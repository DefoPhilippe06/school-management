from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenue {user.get_full_name() or user.username} !")

            # Redirection selon le rôle
            if user.role == 'PARENT':
                return redirect('parent_dashboard')
            elif user.role == 'TEACHER':
                return redirect('dashboard')  # on créera le portail enseignant ensuite
            else:
                return redirect('dashboard')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect('login')


@login_required
def dashboard(request):
    context = {
        'user': request.user,
    }

    if request.user.role == 'ADMIN' or request.user.is_superuser:
        from students.models import Student
        from teachers.models import Teacher
        from classes.models import ClassRoom, Level
        from core.models import SchoolYear
        from subjects.models import Subject

        current_year = SchoolYear.objects.filter(is_current=True).first()

        context.update({
            'total_students': Student.objects.count(),
            'total_teachers': Teacher.objects.count(),
            'total_classes': ClassRoom.objects.filter(school_year=current_year).count() if current_year else 0,
            'current_year': current_year,
            'classes': ClassRoom.objects.filter(school_year=current_year).select_related('level') if current_year else [],
            'levels': Level.objects.all(),
            'subjects': Subject.objects.all(),
        })

    return render(request, 'accounts/dashboard.html', context)

    return render(request, 'accounts/dashboard.html', context)
@login_required
def parent_dashboard(request):
    if request.user.role != 'PARENT':
        messages.warning(request, "Accès réservé aux parents.")
        return redirect('dashboard')

    try:
        parent = request.user.parent_profile
        children = parent.students.select_related('user', 'current_class').all()
    except:
        children = []

    context = {
        'children': children,
    }
    return render(request, 'accounts/parent_dashboard.html', context)

@login_required
def teacher_dashboard(request):
    if request.user.role != 'TEACHER' and not request.user.is_superuser:
        messages.warning(request, "Accès réservé aux enseignants.")
        return redirect('dashboard')

    try:
        teacher = request.user.teacher_profile
        subjects = teacher.subjects.all()
    except:
        teacher = None
        subjects = []

    context = {
        'teacher': teacher,
        'subjects': subjects,
    }
    return render(request, 'accounts/teacher_dashboard.html', context)

from .models import Notification
from django.http import JsonResponse


@login_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    
    # Si on vient d'un lien, on redirige
    if notif.link:
        return redirect(notif.link)
    return redirect('dashboard')


@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, "Toutes les notifications ont été marquées comme lues.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))