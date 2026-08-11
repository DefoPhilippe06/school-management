from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student
from .tasks import send_student_credentials


@receiver(post_save, sender=Student)
def student_created(sender, instance, created, **kwargs):
    if created:
        # Récupérer les emails des parents
        parent_emails = list(
            instance.parents.filter(user__email__isnull=False)
            .exclude(user__email='')
            .values_list('user__email', flat=True)
        )

        if parent_emails:
            # Lancer la tâche Celery
            send_student_credentials.delay(instance.id, parent_emails)