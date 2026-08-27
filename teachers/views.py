from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from accounts.decorators import role_required
from accounts.password_utils import generate_password, send_credentials_email
from .models import Teacher
from classes.models import ClassRoom
from subjects.models import Subject
from core.models import SchoolYear

User = get_user_model()


@login_required
@role_required('ADMIN')
def teacher_list(request):
    teachers = Teacher.objects.select_related('user').prefetch_related('classes', 'subjects').all()
    current_year = SchoolYear.objects.filter(is_current=True).first()
    classes = ClassRoom.objects.filter(school_year=current_year) if current_year else []
    subjects = Subject.objects.all()

    return render(request, 'teachers/teacher_list.html', {
        'teachers': teachers,
        'classes': classes,
        'subjects': subjects,
    })


@login_required
@role_required('ADMIN')
def teacher_save(request):
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        matricule = request.POST.get('matricule')
        specialization = request.POST.get('specialization', '')
        phone = request.POST.get('phone', '')
        class_ids = request.POST.getlist('classes')
        subject_ids = request.POST.getlist('subjects')

        if teacher_id:
            # Modification
            teacher = get_object_or_404(Teacher, id=teacher_id)
            user = teacher.user
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()

            teacher.matricule = matricule
            teacher.specialization = specialization
            teacher.phone = phone
            teacher.save()

            teacher.classes.set(class_ids)
            # Les matières sont liées via Subject.teachers (ManyToMany inverse)
            for subject in Subject.objects.all():
                if str(subject.id) in subject_ids:
                    subject.teachers.add(teacher)
                else:
                    subject.teachers.remove(teacher)

            messages.success(request, f"Enseignant {user.get_full_name()} modifié.")
        else:
            # Création
            if User.objects.filter(username=username).exists():
                messages.error(request, "Ce nom d'utilisateur existe déjà.")
                return redirect('teacher_list')
            if Teacher.objects.filter(matricule=matricule).exists():
                messages.error(request, "Ce matricule existe déjà.")
                return redirect('teacher_list')

            raw_password = generate_password()
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=User.Role.TEACHER,
                password=raw_password,
            )

            teacher = Teacher.objects.create(
                user=user,
                matricule=matricule,
                specialization=specialization,
                phone=phone
            )
            teacher.classes.set(class_ids)

            for sid in subject_ids:
                subject = Subject.objects.get(id=sid)
                subject.teachers.add(teacher)

            email_sent = send_credentials_email(user, raw_password)
            if email_sent:
                messages.success(
                    request,
                    f"Enseignant {user.get_full_name()} créé. Identifiants envoyés à {email}."
                )
            else:
                messages.success(
                    request,
                    f"Enseignant {user.get_full_name()} créé. Mot de passe : {raw_password} "
                    f"(aucun email — notez-le)."
                )

    return redirect('teacher_list')


@login_required
@role_required('ADMIN')
def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    name = teacher.user.get_full_name()
    user = teacher.user
    teacher.delete()
    user.delete()
    messages.success(request, f"Enseignant {name} supprimé.")
    return redirect('teacher_list')