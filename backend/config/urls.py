"""
URL configuration for Legal Metrology Compliance Inspection System.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import HealthCheckView

urlpatterns = [
    # Administration portal
    path('admin/', admin.site.urls),

    # Health check endpoint for system monitoring & verification
    path('api/health/', HealthCheckView.as_view(), name='api-health'),

    # User & officer authentication endpoints
    path('api/users/', include('users.urls')),

    # Scanner app placeholders (future prompt expansion)
    path('api/scanner/', include('scanner.urls')),

    # Compliance rule engine placeholders (future prompt expansion)
    path('api/compliance/', include('compliance.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
