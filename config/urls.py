from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', lambda request: redirect('dashboard')),
    path('students/', include('students.urls')),
    path('grades/', include('grades.urls')),
    path('classes/', include('classes.urls')),
    path('attendance/', include('attendance.urls')),
    path('subjects/', include('subjects.urls')),
    path('teachers/', include('teachers.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include

# garde tes urls actuelles, et ajoute :
urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),
]    
