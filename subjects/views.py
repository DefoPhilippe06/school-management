from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import Subject

@login_required
@role_required('ADMIN')
def subject_list(request):
    subjects = Subject.objects.all().order_by('name')
    return render(request, 'subjects/subject_list.html', {'subjects': subjects})


@login_required
@role_required('ADMIN')
def subject_save(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        name = request.POST.get('name').strip()
        code = request.POST.get('code').strip().upper()
        coefficient = request.POST.get('coefficient', 1)

        if subject_id:
            subject = get_object_or_404(Subject, id=subject_id)
            subject.name = name
            subject.code = code
            subject.coefficient = coefficient
            subject.save()
            messages.success(request, f"Matière « {name} » modifiée.")
        else:
            if Subject.objects.filter(code=code).exists():
                messages.error(request, f"Le code « {code} » existe déjà.")
            else:
                Subject.objects.create(name=name, code=code, coefficient=coefficient)
                messages.success(request, f"Matière « {name} » créée.")

    return redirect('dashboard')


@login_required
@role_required('ADMIN')
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    name = subject.name
    subject.delete()
    messages.success(request, f"Matière « {name} » supprimée.")
    return redirect('dashboard')