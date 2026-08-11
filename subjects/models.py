from django.db import models
from teachers.models import Teacher
from classes.models import Level


class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom de la matière")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    coefficient = models.DecimalField(max_digits=3, decimal_places=1, default=1.0, verbose_name="Coefficient")
    levels = models.ManyToManyField(Level, related_name='subjects', verbose_name="Niveaux concernés")
    teachers = models.ManyToManyField(Teacher, related_name='subjects', blank=True, verbose_name="Enseignants")

    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"
