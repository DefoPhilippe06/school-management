from .models import User, Notification


def notify_admins(message, link='', exclude_user=None):
    """Notifie tous les administrateurs."""
    admins = User.objects.filter(role=User.Role.ADMIN, is_active=True)
    if exclude_user is not None:
        admins = admins.exclude(pk=exclude_user.pk)

    notifs = [
        Notification(recipient=a, message=message[:255], link=link or '')
        for a in admins
    ]
    if notifs:
        Notification.objects.bulk_create(notifs)