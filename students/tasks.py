from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from datetime import datetime
from io import BytesIO
import secrets
import string
import pandas as pd

from .models import Student, Enrollment
from classes.models import ClassRoom
from core.models import SchoolYear

User = get_user_model()


def generate_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


@shared_task
def send_student_credentials(student_id, parent_emails):
    """
    Génère un mot de passe pour l'élève et l'envoie par email aux parents.
    """
    try:
        student = Student.objects.select_related('user').get(id=student_id)
        user = student.user

        # Générer un mot de passe
        raw_password = generate_password()
        user.password = make_password(raw_password)
        user.save()

        # Contenu de l'email
        subject = f"Identifiants de connexion - {student.user.get_full_name()}"
        message = f"""
Bonjour,

Votre enfant {student.user.get_full_name()} (Matricule : {student.matricule}) a été inscrit dans notre établissement.

Voici ses identifiants de connexion :

Nom d'utilisateur : {user.username}
Mot de passe      : {raw_password}

Nous vous recommandons de changer ce mot de passe dès la première connexion.

Cordialement,
L'administration
"""

        # Envoi aux parents
        for email in parent_emails:
            if email:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

        return f"Email envoyé pour {student.matricule}"
    except Exception as e:
        return f"Erreur : {str(e)}"


@shared_task(bind=True)
def import_students_task(self, file_content, filename, admin_email, admin_id):
    """
    Importe les élèves depuis un fichier Excel/CSV en arrière-plan.
    Un échec sur une ligne n'arrête pas le processus.
    """
    success_count = 0
    error_count = 0
    errors = []

    try:
        # Lire le fichier
        if filename.lower().endswith('.csv'):
            df = pd.read_csv(BytesIO(file_content))
        else:
            df = pd.read_excel(BytesIO(file_content))

        # Normaliser les noms de colonnes
        df.columns = [str(col).strip().lower() for col in df.columns]

        current_year = SchoolYear.objects.filter(is_current=True).first()

        for index, row in df.iterrows():
            row_num = index + 2  # +2 car Excel commence à 1 + en-tête
            try:
                first_name = str(row.get('prenom') or row.get('prénom') or row.get('first_name') or '').strip()
                last_name = str(row.get('nom') or row.get('last_name') or '').strip()
                matricule = str(row.get('matricule') or '').strip()
                gender_raw = str(row.get('sexe') or row.get('gender') or 'M').strip().upper()
                dob_raw = row.get('date_naissance') or row.get('date_of_birth') or row.get('date de naissance')
                place_of_birth = str(row.get('lieu_naissance') or row.get('place_of_birth') or '').strip()
                phone = str(row.get('telephone') or row.get('phone') or '').strip()
                address = str(row.get('adresse') or row.get('address') or '').strip()
                class_name = str(row.get('classe') or row.get('class') or '').strip()

                if not first_name or not last_name or not matricule:
                    raise ValueError("Prénom, Nom ou Matricule manquant")

                # Normaliser le sexe
                if gender_raw in ['F', 'FEMININ', 'FEMME', 'FÉMININ']:
                    gender = 'F'
                else:
                    gender = 'M'

                # Date de naissance
                if pd.isna(dob_raw) or not dob_raw:
                    raise ValueError("Date de naissance manquante")

                if isinstance(dob_raw, str):
                    date_of_birth = None
                    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d'):
                        try:
                            date_of_birth = datetime.strptime(dob_raw, fmt).date()
                            break
                        except ValueError:
                            continue
                    if not date_of_birth:
                        raise ValueError(f"Format de date invalide : {dob_raw}")
                else:
                    date_of_birth = pd.to_datetime(dob_raw).date()

                # Vérifier matricule unique
                if Student.objects.filter(matricule=matricule).exists():
                    raise ValueError(f"Matricule {matricule} déjà existant")

                # Username unique
                username = f"{first_name.lower()}.{last_name.lower()}".replace(' ', '')
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1

                # Créer l'utilisateur
                user = User.objects.create_user(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    role=User.Role.STUDENT,
                    password='Temp1234'
                )

                # Trouver la classe
                classroom = None
                if class_name and current_year:
                    classroom = ClassRoom.objects.filter(
                        name__iexact=class_name,
                        school_year=current_year
                    ).first()

                # Créer l'élève
                student = Student.objects.create(
                    user=user,
                    matricule=matricule,
                    gender=gender,
                    date_of_birth=date_of_birth,
                    place_of_birth=place_of_birth,
                    phone=phone,
                    address=address,
                    current_class=classroom
                )

                # Inscription
                if classroom and current_year:
                    Enrollment.objects.get_or_create(
                        student=student,
                        school_year=current_year,
                        defaults={'classroom': classroom, 'status': 'ACTIVE'}
                    )

                success_count += 1

            except Exception as e:
                error_count += 1
                errors.append(f"Ligne {row_num} : {str(e)}")

        # Email de confirmation
        subject = f"Import élèves terminé — {success_count} réussis, {error_count} échecs"
        message = f"""
Bonjour,

L'import des élèves est terminé.

Résumé :
• Élèves importés avec succès : {success_count}
• Échecs : {error_count}

"""
        if errors:
            message += "Détails des erreurs :\n"
            for err in errors[:30]:
                message += f"  - {err}\n"
            if len(errors) > 30:
                message += f"  ... et {len(errors) - 30} autres erreurs.\n"

        message += "\nCordialement,\nSystème de Gestion Scolaire"

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            fail_silently=False,
        )

        return {
            'success': success_count,
            'errors': error_count,
            'details': errors
        }

    except Exception as e:
        send_mail(
            "Échec de l'import des élèves",
            f"Une erreur critique est survenue lors de l'import :\n\n{str(e)}",
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            fail_silently=True,
        )
        raise