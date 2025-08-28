"""
FamilyHub Development Tracker URL Configuration

URL patterns for the Django development tracker application.
Provides comprehensive routing for project management, task tracking,
artifact versioning, and development progress monitoring.

Main URL Structure:
- /admin/ - Django admin interface
- /accounts/ - User authentication (login/logout)
- /tracker/ - Main application (dashboard, projects, apps, tasks)
- /api/ - RESTful API endpoints for AJAX functionality

Static and media files are served during development.
For production deployment, configure web server to serve static files.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

# Configure admin site headers
admin.site.site_header = "FamilyHub Development Tracker Admin"
admin.site.site_title = "Dev Tracker Admin"
admin.site.index_title = "Welcome to FamilyHub Development Tracker Administration"

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # User accounts app
    path('accounts/', include('accounts.urls')),
    
    # Main application URLs
    path('tracker/', include('tracker.urls')),
    
    # API endpoints (included in tracker app)
    path('api/', include('tracker.api_urls', namespace='api')),
    
    # Root redirect to dashboard
    path('', RedirectView.as_view(url='/tracker/', permanent=False)),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
