from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from . import realtime

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("homepage/", include("homepage.urls", namespace="homepage")),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path('events/', realtime.event_stream, name='events'),
]

# Serve media files (in production, consider using cloud storage or nginx)
# For now, serve via Django - in production, configure your web server to serve /media/
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
