from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from students.models import Student
from subjects.models import Subject
from core.models import SchoolYear
from accounts.models import User


class SequenceGrade(models.Model):
    """Note d'une séquence (1 à 6)"""
    
    class Sequence(models.IntegerChoices):
        SEQ_1 = 1, 'Séquence 1'
        SEQ_2 = 2, 'Séquence 2'
        SEQ_3 = 3, 'Séquence 3'
        SEQ_4 = 4, 'Séquence 4'
        SEQ_5 = 5, 'Séquence 5'
        SEQ_6 = 6, 'Séquence 6'

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='sequence_grades',
        verbose_name="Élève"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='sequence_grades',
        verbose_name="Matière"
    )
    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.CASCADE,
        related_name='sequence_grades',
        verbose_name="Année scolaire"
    )
    sequence = models.PositiveSmallIntegerField(
        choices=Sequence.choices,
        verbose_name="Séquence"
    )
    score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        verbose_name="Note (/20)"
    )
    appreciation = models.CharField(max_length=100, blank=True, verbose_name="Appréciation")
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sequence_grades_created',
        verbose_name="Saisi par"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Note de séquence"
        verbose_name_plural = "Notes de séquence"
        unique_together = ('student', 'subject', 'school_year', 'sequence')
        ordering = ['student', 'subject', 'sequence']

    def __str__(self):
        return f"{self.student} - {self.subject} - S{self.sequence}: {self.score}/20"

    @property
    def trimester(self):
        """Retourne le numéro du trimestre (1, 2 ou 3)"""
        if self.sequence in [1, 2]:
            return 1
        elif self.sequence in [3, 4]:
            return 2
        return 3


class TrimesterAverage:
    """Classe utilitaire pour calculer les moyennes de trimestre"""

    @staticmethod
    def get_trimester_sequences(trimester: int) -> list:
        mapping = {
            1: [1, 2],
            2: [3, 4],
            3: [5, 6],
        }
        return mapping.get(trimester, [])

    @staticmethod
    def calculate(student, subject, school_year, trimester: int):
        sequences = TrimesterAverage.get_trimester_sequences(trimester)
        grades = SequenceGrade.objects.filter(
            student=student,
            subject=subject,
            school_year=school_year,
            sequence__in=sequences
        )

        if not grades.exists():
            return None

        total = sum(g.score for g in grades)
        return round(total / grades.count(), 2)