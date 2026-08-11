from django.db import models
from accounts.models import User
from classes.models import ClassRoom
from core.models import SchoolYear


class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'role': User.Role.STUDENT},
        verbose_name="Compte utilisateur"
    )
    matricule = models.CharField(max_length=30, unique=True, verbose_name="Matricule")
    date_of_birth = models.DateField(verbose_name="Date de naissance")
    place_of_birth = models.CharField(max_length=100, blank=True, verbose_name="Lieu de naissance")
    gender = models.CharField(
        max_length=10,
        choices=[('M', 'Masculin'), ('F', 'Féminin')],
        verbose_name="Sexe"
    )
    address = models.TextField(blank=True, verbose_name="Adresse")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    photo = models.ImageField(upload_to='students/photos/', blank=True, null=True, verbose_name="Photo")

    # Lien avec la classe actuelle
    current_class = models.ForeignKey(
        ClassRoom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name="Classe actuelle"
    )

    class Meta:
        verbose_name = "Élève"
        verbose_name_plural = "Élèves"
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.matricule})"


class Parent(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='parent_profile',
        limit_choices_to={'role': User.Role.PARENT},
        verbose_name="Compte utilisateur"
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    address = models.TextField(blank=True, verbose_name="Adresse")
    profession = models.CharField(max_length=100, blank=True, verbose_name="Profession")
    
    # Un parent peut avoir plusieurs enfants
    students = models.ManyToManyField(
        Student,
        related_name='parents',
        blank=True,
        verbose_name="Enfants"
    )

    class Meta:
        verbose_name = "Parent"
        verbose_name_plural = "Parents"
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Actif'
        TRANSFERRED = 'TRANSFERRED', 'Transféré'
        WITHDRAWN = 'WITHDRAWN', 'Désisté'
        GRADUATED = 'GRADUATED', 'Diplômé'

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Élève"
    )
    classroom = models.ForeignKey(
        'classes.ClassRoom',
        on_delete=models.PROTECT,
        related_name='enrollments',
        verbose_name="Classe"
    )
    school_year = models.ForeignKey(
        'core.SchoolYear',
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Année scolaire"
    )
    enrollment_date = models.DateField(auto_now_add=True, verbose_name="Date d'inscription")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Statut"
    )
    remarks = models.TextField(blank=True, verbose_name="Observations")

    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        unique_together = ('student', 'school_year')
        ordering = ['-school_year', 'classroom', 'student']

    def __str__(self):
        return f"{self.student} → {self.classroom} ({self.school_year})"