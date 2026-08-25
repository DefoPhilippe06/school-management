from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(recipient=request.user, is_read=False)
        return {
            'unread_notifications': unread,
            'unread_count': unread.count()
        }
    return {
        'unread_notifications': [],
        'unread_count': 0
    }
def school_stats(request):
    from students.models import Student
    from teachers.models import Teacher
    from classes.models import ClassRoom
    from core.models import SchoolYear

    current_year = SchoolYear.objects.filter(is_current=True).first()
    return {
        'footer_students': Student.objects.count(),
        'footer_teachers': Teacher.objects.count(),
        'footer_classes': ClassRoom.objects.filter(school_year=current_year).count() if current_year else 0,
    }