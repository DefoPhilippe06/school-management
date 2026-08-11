from django.db import models
from accounts.models import User


class Teacher(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile',
        limit_choices_to={'role': User.Role.TEACHER},
        verbose_name="Compte utilisateur"
    )
    matricule = models.CharField(max_length=30, unique=True, verbose_name="Matricule")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    address = models.TextField(blank=True, verbose_name="Adresse")
    specialization = models.CharField(max_length=100, blank=True, verbose_name="Spécialité")
    hire_date = models.DateField(null=True, blank=True, verbose_name="Date d'embauche")
    photo = models.ImageField(upload_to='teachers/photos/', blank=True, null=True, verbose_name="Photo")
    classes = models.ManyToManyField(
        'classes.ClassRoom',
        related_name='teachers',
        blank=True,
        verbose_name="Classes enseignées"
    )

    class Meta:
        verbose_name = "Enseignant"
        verbose_name_plural = "Enseignants"
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.matricule})"