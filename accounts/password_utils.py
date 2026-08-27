import secrets
import string
from django.core.mail import send_mail
from django.conf import settings


def generate_password(length=12):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_credentials_email(user, raw_password):
    """Envoie les identifiants si l'utilisateur a un email."""
    if not user.email:
        return False
    subject = "Vos identifiants de connexion — School Management"
    message = f"""Bonjour {user.get_full_name() or user.username},

Votre compte a été créé sur School Management.

Identifiants :
• Nom d'utilisateur : {user.username}
• Mot de passe      : {raw_password}

Changez ce mot de passe dès la première connexion.

Cordialement,
L'administration
"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )
        return True
    except Exception:
        return False