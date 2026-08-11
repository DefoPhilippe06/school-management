from django.http import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template import context
from .models import SequenceGrade
from students.models import Student
from subjects.models import Subject
from core.models import SchoolYear
from classes.models import ClassRoom
from accounts.decorators import role_required


@login_required
@role_required('ADMIN', 'TEACHER')
def grade_entry(request):
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
        # Admin voit tout
        classes = ClassRoom.objects.filter(school_year=current_year) if current_year else []
        subjects = Subject.objects.all()

    selected_class = request.GET.get('class')
    selected_subject = request.GET.get('subject')
    selected_sequence = request.GET.get('sequence')

    students = []
    if selected_class and selected_subject and selected_sequence:
        students = Student.objects.filter(current_class_id=selected_class).select_related('user')

    context = {
        'classes': classes,
        'subjects': subjects,
        'sequences': SequenceGrade.Sequence.choices,
        'students': students,
        'selected_class': selected_class,
        'selected_subject': selected_subject,
        'selected_sequence': selected_sequence,
        'current_year': current_year,
    }
    return render(request, 'grades/grade_entry.html', context)

@role_required('ADMIN', 'TEACHER')
def grade_save(request):
    if request.method == 'POST':
        class_id = request.POST.get('class')
        subject_id = request.POST.get('subject')
        sequence = request.POST.get('sequence')
        year_id = request.POST.get('year')

        current_year = get_object_or_404(SchoolYear, id=year_id)
        subject = get_object_or_404(Subject, id=subject_id)

        for key, value in request.POST.items():
            if key.startswith('score_'):
                student_id = key.split('_')[1]
                if value.strip():
                    student = get_object_or_404(Student, id=student_id)
                    SequenceGrade.objects.update_or_create(
                        student=student,
                        subject=subject,
                        school_year=current_year,
                        sequence=sequence,
                        defaults={
                            'score': value,
                            'created_by': request.user
                        }
                    )

        messages.success(request, "Notes enregistrées avec succès.")
        return redirect(f"/grades/?class={class_id}&subject={subject_id}&sequence={sequence}")

    return redirect('grade_entry')

@login_required
@role_required('ADMIN', 'TEACHER', 'PARENT', 'STUDENT')
def student_grades(request, student_id):
    from collections import defaultdict
    from decimal import Decimal

    student = get_object_or_404(
        Student.objects.select_related('user', 'current_class'),
        id=student_id
    )
    current_year = SchoolYear.objects.filter(is_current=True).first()

    grades = SequenceGrade.objects.filter(
        student=student,
        school_year=current_year
    ).select_related('subject').order_by('subject__name', 'sequence')

    # Organiser par matière
    subjects_data = defaultdict(lambda: {
        'sequences': {},
        'trimesters': {},
        'coefficient': None,
        'annual': None
    })

    for g in grades:
        subjects_data[g.subject]['sequences'][g.sequence] = g.score
        subjects_data[g.subject]['coefficient'] = g.subject.coefficient

    # Calcul des trimestres et moyenne annuelle
    for subject, data in subjects_data.items():
        seq = data['sequences']

        # Trimestre 1 = (S1 + S2) / 2
        t1_notes = [seq.get(1), seq.get(2)]
        t1_notes = [n for n in t1_notes if n is not None]
        data['trimesters'][1] = round(sum(t1_notes) / len(t1_notes), 2) if t1_notes else None

        # Trimestre 2 = (S3 + S4) / 2
        t2_notes = [seq.get(3), seq.get(4)]
        t2_notes = [n for n in t2_notes if n is not None]
        data['trimesters'][2] = round(sum(t2_notes) / len(t2_notes), 2) if t2_notes else None

        # Trimestre 3 = (S5 + S6) / 2
        t3_notes = [seq.get(5), seq.get(6)]
        t3_notes = [n for n in t3_notes if n is not None]
        data['trimesters'][3] = round(sum(t3_notes) / len(t3_notes), 2) if t3_notes else None

        # Moyenne annuelle = moyenne des 3 trimestres
        trim_notes = [data['trimesters'].get(1), data['trimesters'].get(2), data['trimesters'].get(3)]
        trim_notes = [n for n in trim_notes if n is not None]
        data['annual'] = round(sum(trim_notes) / len(trim_notes), 2) if trim_notes else None

    context = {
        'student': student,
        'current_year': current_year,
        'subjects_data': dict(subjects_data),
    }
    return render(request, 'grades/student_grades.html', context)
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.db.models import Avg, Count
from attendance.models import Attendance


@login_required
@role_required('ADMIN', 'TEACHER', 'PARENT', 'STUDENT')
def generate_bulletin_pdf(request, student_id):
    from collections import defaultdict
    from decimal import Decimal
    from django.db.models import Avg

    student = get_object_or_404(
        Student.objects.select_related('user', 'current_class', 'current_class__level'),
        id=student_id
    )
    current_year = SchoolYear.objects.filter(is_current=True).first()
    classroom = student.current_class

    # === Notes de l'élève ===
    grades = SequenceGrade.objects.filter(
        student=student,
        school_year=current_year
    ).select_related('subject')

    subjects_data = defaultdict(lambda: {
        'sequences': {},
        'trimesters': {},
        'coefficient': None,
        'annual': None
    })

    for g in grades:
        subjects_data[g.subject]['sequences'][g.sequence] = g.score
        subjects_data[g.subject]['coefficient'] = g.subject.coefficient

    total_points = Decimal('0')
    total_coef = Decimal('0')

    for subject, data in subjects_data.items():
        seq = data['sequences']

        t1 = [n for n in [seq.get(1), seq.get(2)] if n is not None]
        data['trimesters'][1] = round(sum(t1) / len(t1), 2) if t1 else None

        t2 = [n for n in [seq.get(3), seq.get(4)] if n is not None]
        data['trimesters'][2] = round(sum(t2) / len(t2), 2) if t2 else None

        t3 = [n for n in [seq.get(5), seq.get(6)] if n is not None]
        data['trimesters'][3] = round(sum(t3) / len(t3), 2) if t3 else None

        trim = [n for n in [data['trimesters'].get(1), data['trimesters'].get(2), data['trimesters'].get(3)] if n is not None]
        data['annual'] = round(sum(trim) / len(trim), 2) if trim else None

        if data['annual'] and data['coefficient']:
            total_points += Decimal(str(data['annual'])) * Decimal(str(data['coefficient']))
            total_coef += Decimal(str(data['coefficient']))

    general_average = round(float(total_points / total_coef), 2) if total_coef > 0 else None

    # === Statistiques de la classe (rangs) ===
    class_students = Student.objects.filter(current_class=classroom)
    class_averages = []

    for s in class_students:
        s_grades = SequenceGrade.objects.filter(student=s, school_year=current_year).select_related('subject')
        s_data = defaultdict(lambda: {'sequences': {}, 'coefficient': None})
        for g in s_grades:
            s_data[g.subject]['sequences'][g.sequence] = g.score
            s_data[g.subject]['coefficient'] = g.subject.coefficient

        s_total_points = Decimal('0')
        s_total_coef = Decimal('0')
        for subj, d in s_data.items():
            seq = d['sequences']
            t1 = [n for n in [seq.get(1), seq.get(2)] if n is not None]
            t2 = [n for n in [seq.get(3), seq.get(4)] if n is not None]
            t3 = [n for n in [seq.get(5), seq.get(6)] if n is not None]
            trims = []
            if t1: trims.append(sum(t1)/len(t1))
            if t2: trims.append(sum(t2)/len(t2))
            if t3: trims.append(sum(t3)/len(t3))
            annual = sum(trims)/len(trims) if trims else None
            if annual and d['coefficient']:
                s_total_points += Decimal(str(annual)) * Decimal(str(d['coefficient']))
                s_total_coef += Decimal(str(d['coefficient']))

        avg = float(s_total_points / s_total_coef) if s_total_coef > 0 else 0
        class_averages.append({'student': s, 'average': avg})

    class_averages.sort(key=lambda x: x['average'], reverse=True)

    rank = None
    for i, item in enumerate(class_averages, 1):
        if item['student'].id == student.id:
            rank = i
            break

    class_first = class_averages[0]['average'] if class_averages else None
    class_last = class_averages[-1]['average'] if class_averages else None
    class_size = len(class_averages)

        # Absences (justifiées et non justifiées)
    from django.db.models import Sum
    from attendance.models import Attendance

    justified_hours = Attendance.objects.filter(
        student=student,
        school_year=current_year,
        status='JUSTIFIED'
    ).aggregate(total=Sum('hours'))['total'] or 0

    unjustified_hours = Attendance.objects.filter(
        student=student,
        school_year=current_year,
        status='UNJUSTIFIED'
    ).aggregate(total=Sum('hours'))['total'] or 0

        # Récupérer les paramètres de l'établissement
    from core.models import SchoolSettings
    school = SchoolSettings.objects.first()

    context = {
        'student': student,
        'current_year': current_year,
        'classroom': classroom,
        'subjects_data': dict(subjects_data),
        'general_average': general_average,
        'rank': rank,
        'class_size': class_size,
        'class_first': class_first,
        'class_last': class_last,
        'justified_hours': justified_hours,
            'unjustified_hours': unjustified_hours,
        'school': school,
        'school_name': school.name if school else "ÉTABLISSEMENT SCOLAIRE",
        'school_city': school.city if school else "Cameroun",
    }

    html_string = render_to_string('grades/bulletin_pdf.html', context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="bulletin_{student.matricule}.pdf"'
    return response