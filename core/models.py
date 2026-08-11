from django.db import models

class SchoolYear(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name="Année scolaire")
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(verbose_name="Date de fin")
    is_current = models.BooleanField(default=False, verbose_name="Année en cours")

    class Meta:
        verbose_name = "Année scolaire"
        verbose_name_plural = "Années scolaires"
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            # S'assurer qu'il n'y a qu'une seule année en cours
            SchoolYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)



class SchoolSettings(models.Model):
    name = models.CharField(max_length=200, default="ÉTABLISSEMENT SCOLAIRE", verbose_name="Nom de l'établissement")
    city = models.CharField(max_length=100, default="Cameroun", verbose_name="Ville / Pays")
    logo = models.ImageField(upload_to='school/', blank=True, null=True, verbose_name="Logo")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.TextField(blank=True, verbose_name="Adresse")

    class Meta:
        verbose_name = "Paramètres de l'établissement"
        verbose_name_plural = "Paramètres de l'établissement"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # On ne garde qu'une seule instance
        self.pk = 1
        super().save(*args, **kwargs)