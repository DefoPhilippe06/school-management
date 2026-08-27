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

from django.contrib.auth import get_user_model
from accounts.decorators import role_required
from accounts.password_utils import generate_password, send_credentials_email

User = get_user_model()


@login_required
@role_required('ADMIN')
def admin_list(request):
    admins = User.objects.filter(role=User.Role.ADMIN).order_by('last_name', 'first_name')
    return render(request, 'accounts/admin_list.html', {'admins': admins})


@login_required
@role_required('ADMIN')
def admin_save(request):
    if request.method == 'POST':
        admin_id = request.POST.get('admin_id')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()

        if admin_id:
            admin = get_object_or_404(User, id=admin_id, role=User.Role.ADMIN)
            admin.first_name = first_name
            admin.last_name = last_name
            admin.email = email
            if username and username != admin.username:
                if User.objects.filter(username=username).exclude(pk=admin.pk).exists():
                    messages.error(request, "Ce nom d'utilisateur existe déjà.")
                    return redirect('admin_list')
                admin.username = username
            admin.save()
            messages.success(request, f"Administrateur {admin.get_full_name()} modifié.")
        else:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Ce nom d'utilisateur existe déjà.")
                return redirect('admin_list')

            raw_password = generate_password()
            admin = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=User.Role.ADMIN,
                password=raw_password,
            )
            email_sent = send_credentials_email(admin, raw_password)
            if email_sent:
                messages.success(
                    request,
                    f"Admin {admin.get_full_name()} créé. Identifiants envoyés à {email}."
                )
            else:
                messages.success(
                    request,
                    f"Admin {admin.get_full_name()} créé. Mot de passe : {raw_password} "
                    f"(aucun email — notez-le)."
                )

    return redirect('admin_list')


@login_required
@role_required('ADMIN')
def admin_delete(request, pk):
    admin = get_object_or_404(User, pk=pk, role=User.Role.ADMIN)
    if admin.pk == request.user.pk:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('admin_list')
    name = admin.get_full_name() or admin.username
    admin.delete()
    messages.success(request, f"Administrateur {name} supprimé.")
    return redirect('admin_list')