from django.db import models
from core.models import SchoolYear


class Level(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Niveau")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"
        ordering = ['order']

    def __str__(self):
        return self.name


class ClassRoom(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nom de la classe")
    level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name='classes', verbose_name="Niveau")
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='classes', verbose_name="Année scolaire")
    capacity = models.PositiveSmallIntegerField(default=40, verbose_name="Capacité maximale")

    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        unique_together = ('name', 'school_year')
        ordering = ['level__order', 'name']

    def __str__(self):
        return f"{self.name} ({self.school_year})"



class TimeSlot(models.Model):
    class Day(models.TextChoices):
        LUNDI = 'LUNDI', 'Lundi'
        MARDI = 'MARDI', 'Mardi'
        MERCREDI = 'MERCREDI', 'Mercredi'
        JEUDI = 'JEUDI', 'Jeudi'
        VENDREDI = 'VENDREDI', 'Vendredi'
        SAMEDI = 'SAMEDI', 'Samedi'

    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='timeslots', verbose_name="Classe")
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, verbose_name="Matière")
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Enseignant")
    day = models.CharField(max_length=10, choices=Day.choices, verbose_name="Jour")
    start_time = models.TimeField(verbose_name="Heure de début")
    end_time = models.TimeField(verbose_name="Heure de fin")
    room = models.CharField(max_length=50, blank=True, verbose_name="Salle")

    class Meta:
        verbose_name = "Créneau horaire"
        verbose_name_plural = "Emploi du temps"
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.classroom} - {self.day} {self.start_time}-{self.end_time} : {self.subject}"    