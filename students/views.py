from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Student
from .forms import StudentRegistrationForm
from classes.models import ClassRoom
from core.models import SchoolYear
from accounts.decorators import role_required

@login_required
@role_required('ADMIN', 'TEACHER')
def student_list(request):
    students = Student.objects.select_related('user', 'current_class', 'current_class__level').all()

    query = request.GET.get('q', '')
    if query:
        students = students.filter(
            Q(matricule__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        )

    class_id = request.GET.get('class')
    if class_id:
        students = students.filter(current_class_id=class_id)

    current_year = SchoolYear.objects.filter(is_current=True).first()
    classes = ClassRoom.objects.filter(school_year=current_year) if current_year else []

    context = {
        'students': students,
        'classes': classes,
        'query': query,
        'selected_class': class_id,
    }
    return render(request, 'students/student_list.html', context)


@login_required
@role_required('ADMIN')
def student_create(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Élève {student.user.get_full_name()} inscrit avec succès.")
            return redirect('student_list')
    else:
        form = StudentRegistrationForm()

    return render(request, 'students/student_form.html', {'form': form})

from django.contrib.auth import get_user_model
User = get_user_model()

@login_required
@role_required('ADMIN')
def student_save(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        matricule = request.POST.get('matricule')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        place_of_birth = request.POST.get('place_of_birth', '')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address', '')
        classroom_id = request.POST.get('classroom')

        if student_id:
            # Modification
            student = get_object_or_404(Student, id=student_id)
            user = student.user
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            student.matricule = matricule
            student.gender = gender
            student.date_of_birth = date_of_birth
            student.place_of_birth = place_of_birth
            student.phone = phone
            student.address = address
            if classroom_id:
                student.current_class_id = classroom_id
            student.save()
            messages.success(request, f"Élève {user.get_full_name()} modifié.")
        else:
            messages.error(request, "Utilisez le formulaire d'inscription pour créer un nouvel élève.")
    
    return redirect('student_list')


@login_required
@role_required('ADMIN')
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    name = student.user.get_full_name()
    user = student.user
    student.delete()
    user.delete()
    messages.success(request, f"Élève {name} supprimé.")
    return redirect('student_list')

from django.core.files.uploadedfile import InMemoryUploadedFile
from .tasks import import_students_task


@login_required
@role_required('ADMIN')
def student_import(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            messages.error(request, "Aucun fichier sélectionné.")
            return redirect('student_list')

        allowed_extensions = ['.xlsx', '.xls', '.csv']
        if not any(uploaded_file.name.lower().endswith(ext) for ext in allowed_extensions):
            messages.error(request, "Format non supporté. Utilisez .xlsx, .xls ou .csv")
            return redirect('student_list')

        file_content = uploaded_file.read()
        admin_email = request.user.email or 'dphilippejunior@gmail.com'

        from .tasks import import_students_task

        try:
            result = import_students_task.run(
                file_content=file_content,
                filename=uploaded_file.name,
                admin_email=admin_email,
                admin_id=request.user.id
            ) or {}
            messages.success(
                request,
                f"Import terminé : {result.get('success', 0)} réussis, "
                f"{result.get('errors', 0)} échecs. Un email a été envoyé à {admin_email}."
            )
        except Exception as e:
            messages.error(request, f"Erreur pendant l'import / email : {str(e)}")

        return redirect('student_list')

    return redirect('student_list')