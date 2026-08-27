from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from accounts.decorators import role_required
from accounts.password_utils import generate_password, send_credentials_email
from .models import Notification

User = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'TEACHER':
            return redirect('teacher_dashboard')
        if request.user.role == 'PARENT':
            return redirect('parent_dashboard')
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenue {user.get_full_name() or user.username} !")

            if user.role == 'PARENT':
                return redirect('parent_dashboard')
            elif user.role == 'TEACHER':
                return redirect('teacher_dashboard')
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


@login_required
def parent_dashboard(request):
    if request.user.role != 'PARENT':
        messages.warning(request, "Accès réservé aux parents.")
        return redirect('dashboard')

    try:
        parent = request.user.parent_profile
        children = parent.students.select_related('user', 'current_class').all()
    except Exception:
        children = []

    return render(request, 'accounts/parent_dashboard.html', {'children': children})


@login_required
def teacher_dashboard(request):
    if request.user.role != 'TEACHER' and not request.user.is_superuser:
        messages.warning(request, "Accès réservé aux enseignants.")
        return redirect('dashboard')

    try:
        teacher = request.user.teacher_profile
        subjects = teacher.subjects.all()
    except Exception:
        teacher = None
        subjects = []

    return render(request, 'accounts/teacher_dashboard.html', {
        'teacher': teacher,
        'subjects': subjects,
    })


@login_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    if notif.link:
        return redirect(notif.link)
    if request.user.role == 'TEACHER':
        return redirect('teacher_dashboard')
    return redirect('dashboard')


@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, "Toutes les notifications ont été marquées comme lues.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


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


@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if username and username != user.username:
            if User.objects.filter(username=username).exclude(pk=user.pk).exists():
                messages.error(request, "Ce nom d'utilisateur est déjà pris.")
                return redirect('profile_edit')
            user.username = username

        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if new_password:
            if not user.check_password(current_password):
                messages.error(request, "Mot de passe actuel incorrect.")
                return redirect('profile_edit')
            if new_password != confirm_password:
                messages.error(request, "Les nouveaux mots de passe ne correspondent pas.")
                return redirect('profile_edit')
            if len(new_password) < 8:
                messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
                return redirect('profile_edit')
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Profil et mot de passe mis à jour.")
        else:
            user.save()
            messages.success(request, "Profil mis à jour.")

        if user.role == 'TEACHER':
            return redirect('teacher_dashboard')
        if user.role == 'PARENT':
            return redirect('parent_dashboard')
        return redirect('dashboard')

    return render(request, 'accounts/profile_edit.html', {'profile_user': user})