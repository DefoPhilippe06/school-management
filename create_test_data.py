import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User
from students.models import Student, Parent, Enrollment
from teachers.models import Teacher
from subjects.models import Subject
from classes.models import ClassRoom
from core.models import SchoolYear
from datetime import date

year = SchoolYear.objects.filter(is_current=True).first()
classe_6a = ClassRoom.objects.filter(name="6ème A").first()
classe_3a = ClassRoom.objects.filter(name="3ème A").first()
classe_td = ClassRoom.objects.filter(name="Terminale D").first()

print("=== Création des données de test ===\n")

# ========== ENSEIGNANTS ==========
enseignants = [
    ("ens.math", "Marie", "Ngo", "ENS-MATH", "Mathématiques"),
    ("ens.francais", "Jean", "Mbarga", "ENS-FRAN", "Français"),
    ("ens.anglais", "Sophie", "Talla", "ENS-ANGL", "Anglais"),
]

for username, first, last, matricule, spec in enseignants:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"first_name": first, "last_name": last, "role": "TEACHER"}
    )
    if created:
        user.set_password("Test1234")
        user.save()
        print(f"✅ Enseignant créé : {first} {last}")
    else:
        print(f"ℹ️  Enseignant existe déjà : {first} {last}")

    Teacher.objects.get_or_create(
        user=user,
        defaults={"matricule": matricule, "specialization": spec}
    )

# Assigner matières
for code, username in [("MATH", "ens.math"), ("FRAN", "ens.francais"), ("ANGL", "ens.anglais")]:
    subject = Subject.objects.filter(code=code).first()
    teacher = Teacher.objects.filter(user__username=username).first()
    if subject and teacher:
        subject.teachers.add(teacher)

# ========== ÉLÈVES ==========
eleves = [
    ("eleve.kamga", "Jean", "Kamga", "2025-001", "M", classe_6a, date(2013, 3, 15)),
    ("eleve.fouda", "Amina", "Fouda", "2025-002", "F", classe_6a, date(2013, 7, 22)),
    ("eleve.nana", "Paul", "Nana", "2025-003", "M", classe_6a, date(2012, 11, 5)),
    ("eleve.biya", "Grace", "Biya", "2025-004", "F", classe_3a, date(2010, 1, 18)),
    ("eleve.onana", "David", "Onana", "2025-005", "M", classe_3a, date(2010, 9, 30)),
    ("eleve.tchou", "Sarah", "Tchou", "2025-006", "F", classe_td, date(2007, 4, 12)),
    ("eleve.mbe", "Kevin", "Mbe", "2025-007", "M", classe_td, date(2007, 8, 25)),
    ("eleve.ndongo", "Esther", "Ndongo", "2025-008", "F", classe_td, date(2006, 12, 3)),
]

for username, first, last, matricule, gender, classe, dob in eleves:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"first_name": first, "last_name": last, "role": "STUDENT"}
    )
    if created:
        user.set_password("Test1234")
        user.save()

    student, stud_created = Student.objects.get_or_create(
        matricule=matricule,
        defaults={
            "user": user,
            "date_of_birth": dob,
            "gender": gender,
            "current_class": classe
        }
    )
    if stud_created:
        print(f"✅ Élève créé : {first} {last} ({matricule})")
    else:
        print(f"ℹ️  Élève existe déjà : {first} {last} ({matricule})")

    if classe and year:
        Enrollment.objects.get_or_create(
            student=student,
            school_year=year,
            defaults={"classroom": classe, "status": "ACTIVE"}
        )

# ========== PARENTS ==========
parents = [
    ("parent.kamga", "Paul", "Kamga", ["eleve.kamga", "eleve.fouda"]),
    ("parent.nana", "Claire", "Nana", ["eleve.nana"]),
    ("parent.biya", "Robert", "Biya", ["eleve.biya", "eleve.onana"]),
    ("parent.tchou", "Marie", "Tchou", ["eleve.tchou", "eleve.mbe"]),
]

for username, first, last, enfants in parents:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"first_name": first, "last_name": last, "role": "PARENT"}
    )
    if created:
        user.set_password("Test1234")
        user.save()
        print(f"✅ Parent créé : {first} {last}")
    else:
        print(f"ℹ️  Parent existe déjà : {first} {last}")

    parent, _ = Parent.objects.get_or_create(user=user)
    for enf_user in enfants:
        try:
            student = Student.objects.get(user__username=enf_user)
            parent.students.add(student)
        except Student.DoesNotExist:
            pass

print("\n========== RÉSUMÉ ==========")
print(f"Enseignants : {Teacher.objects.count()}")
print(f"Élèves      : {Student.objects.count()}")
print(f"Parents     : {Parent.objects.count()}")
print(f"Utilisateurs totaux : {User.objects.count()}")
print("\nMot de passe de tous les comptes de test : Test1234")