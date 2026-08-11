from django.db import models
from students.models import Student
from subjects.models import Subject
from core.models import SchoolYear
from accounts.models import User


class Attendance(models.Model):
    class Status(models.TextChoices):
        JUSTIFIED = 'JUSTIFIED', 'Justifiée'
        UNJUSTIFIED = 'UNJUSTIFIED', 'Non justifiée'

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="Élève"
    )
    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="Année scolaire"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Matière"
    )
    date = models.DateField(verbose_name="Date")
    hours = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=1.0,
        verbose_name="Nombre d'heures"
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.UNJUSTIFIED,
        verbose_name="Statut"
    )
    reason = models.TextField(blank=True, verbose_name="Motif / Justification")
    sequence = models.PositiveSmallIntegerField(
        null=True, blank=True,
        choices=[(i, f"Séquence {i}") for i in range(1, 7)],
        verbose_name="Séquence"
    )
    
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='attendances_recorded',
        verbose_name="Enregistré par"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Absence"
        verbose_name_plural = "Absences"
        ordering = ['-date']

    def __str__(self):
        return f"{self.student} - {self.date} ({self.hours}h) - {self.get_status_display()}"