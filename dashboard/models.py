from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user profile with timezone and notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    timezone = models.CharField(max_length=100, default='UTC', help_text="User's preferred timezone", choices=[
        ('UTC', 'UTC (Coordinated Universal Time)'),
        ('Asia/Manila', 'Philippines (Manila)'),
        ('America/New_York', 'United States (Eastern Time)'),
        ('America/Chicago', 'United States (Central Time)'),
        ('America/Denver', 'United States (Mountain Time)'),
        ('America/Los_Angeles', 'United States (Pacific Time)'),
        ('Europe/London', 'United Kingdom (London)'),
        ('Europe/Paris', 'France (Paris)'),
        ('Europe/Berlin', 'Germany (Berlin)'),
        ('Europe/Rome', 'Italy (Rome)'),
        ('Europe/Madrid', 'Spain (Madrid)'),
        ('Asia/Tokyo', 'Japan (Tokyo)'),
        ('Asia/Shanghai', 'China (Shanghai)'),
        ('Asia/Hong_Kong', 'Hong Kong'),
        ('Asia/Singapore', 'Singapore'),
        ('Asia/Bangkok', 'Thailand (Bangkok)'),
        ('Asia/Jakarta', 'Indonesia (Jakarta)'),
        ('Asia/Kuala_Lumpur', 'Malaysia (Kuala Lumpur)'),
        ('Asia/Seoul', 'South Korea (Seoul)'),
        ('Asia/Dubai', 'United Arab Emirates (Dubai)'),
        ('Asia/Riyadh', 'Saudi Arabia (Riyadh)'),
        ('Asia/Kolkata', 'India (Mumbai/Delhi)'),
        ('Australia/Sydney', 'Australia (Sydney)'),
        ('Australia/Melbourne', 'Australia (Melbourne)'),
        ('Pacific/Auckland', 'New Zealand (Auckland)'),
        ('America/Toronto', 'Canada (Toronto)'),
        ('America/Vancouver', 'Canada (Vancouver)'),
        ('America/Mexico_City', 'Mexico (Mexico City)'),
        ('America/Sao_Paulo', 'Brazil (São Paulo)'),
        ('America/Buenos_Aires', 'Argentina (Buenos Aires)'),
    ])
    email_notifications = models.BooleanField(default=True)
    web_notifications = models.BooleanField(default=True)
    bio = models.TextField(blank=True, max_length=500, help_text="Short biography or description")
    phone = models.CharField(max_length=20, blank=True, help_text="Phone number")
    location = models.CharField(max_length=100, blank=True, help_text="Location/Country", choices=[
        ('Philippines', 'Philippines'),
        ('United States', 'United States'),
        ('United Kingdom', 'United Kingdom'),
        ('Canada', 'Canada'),
        ('Australia', 'Australia'),
        ('Japan', 'Japan'),
        ('China', 'China'),
        ('Singapore', 'Singapore'),
        ('Malaysia', 'Malaysia'),
        ('Thailand', 'Thailand'),
        ('Indonesia', 'Indonesia'),
        ('South Korea', 'South Korea'),
        ('India', 'India'),
        ('Germany', 'Germany'),
        ('France', 'France'),
        ('Italy', 'Italy'),
        ('Spain', 'Spain'),
        ('Brazil', 'Brazil'),
        ('Mexico', 'Mexico'),
        ('Argentina', 'Argentina'),
        ('New Zealand', 'New Zealand'),
        ('United Arab Emirates', 'United Arab Emirates'),
        ('Saudi Arabia', 'Saudi Arabia'),
        ('Other', 'Other'),
    ])
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, help_text="Profile picture")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class Event(models.Model):
    """Calendar events/meetings"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField(help_text="Stored in UTC")
    end_time = models.DateTimeField(help_text="Stored in UTC")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    location = models.CharField(max_length=200, blank=True)
    external_calendar_id = models.CharField(max_length=200, blank=True, null=True, help_text="ID from external calendar sync")
    external_calendar_type = models.CharField(max_length=50, blank=True, choices=[
        ('google', 'Google Calendar'),
        ('outlook', 'Outlook'),
        ('ical', 'iCal'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['user', 'start_time']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class Reminder(models.Model):
    """Reminders linked to events"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reminders', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    reminder_time = models.DateTimeField(help_text="When to send the reminder (UTC)")
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['reminder_time']
        indexes = [
            models.Index(fields=['user', 'reminder_time', 'is_sent']),
        ]

    def __str__(self):
        return f"Reminder: {self.title} for {self.user.username}"


class Notification(models.Model):
    """Notifications for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=[
        ('reminder', 'Reminder'),
        ('event', 'Event'),
        ('system', 'System'),
    ], default='reminder')
    is_read = models.BooleanField(default=False)
    delivery_method = models.CharField(max_length=50, choices=[
        ('email', 'Email'),
        ('web', 'Web'),
        ('both', 'Both'),
    ], default='web')
    delivery_status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ], default='pending')
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
        ]

    def __str__(self):
        return f"Notification: {self.title} for {self.user.username}"

