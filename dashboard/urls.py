from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("calendar/", views.calendar_view, name="calendar"),
    path("timezone/", views.timezone_conversion_view, name="timezone"),
    path("notifications/", views.notifications_view, name="notifications"),
    path("settings/", views.settings_view, name="settings"),
    path("profile/", views.profile_view, name="profile"),
    path("settings/security-questions/", views.set_security_questions_view, name="set_security_questions"),
    
    # Event management
    path("events/create/", views.create_event_view, name="create_event"),
    path("events/<int:event_id>/edit/", views.edit_event_view, name="edit_event"),
    path("events/<int:event_id>/delete/", views.delete_event_view, name="delete_event"),
    
    # API endpoints
    path("api/events/", views.events_api, name="events_api"),
    path("api/events/<int:event_id>/", views.event_detail_api, name="event_detail_api"),
    path("api/profile/", views.profile_api, name="profile_api"),
]