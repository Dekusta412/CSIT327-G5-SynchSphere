from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from .models import Event, Reminder, UserProfile
import pytz


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with styled fields"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'w-full bg-transparent border-none text-white placeholder-gray-400 focus:outline-none',
            'placeholder': 'Current password',
            'autocomplete': 'current-password'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'w-full bg-transparent border-none text-white placeholder-gray-400 focus:outline-none',
            'placeholder': 'New password',
            'autocomplete': 'new-password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'w-full bg-transparent border-none text-white placeholder-gray-400 focus:outline-none',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password'
        })


class EventForm(forms.ModelForm):
    """Form for creating/editing events"""
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        required=True
    )
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        required=True
    )

    class Meta:
        model = Event
        fields = ['title', 'description', 'invite_participants', 'start_time', 'end_time', 'location']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Event Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Event Description'
            }),
            'invite_participants': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Enter participant emails (comma-separated)\ne.g., user1@example.com, user2@example.com'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Location (optional)'
            }),
        }


class ReminderForm(forms.ModelForm):
    """Form for creating reminders"""
    reminder_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        required=True
    )

    class Meta:
        model = Reminder
        fields = ['title', 'description', 'reminder_time']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Reminder Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Reminder Description'
            }),
        }


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    
    # Country-based timezones with Philippines included
    COUNTRY_TIMEZONES = [
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
    ]
    
    # Location options
    LOCATION_CHOICES = [
        ('', 'Select Location'),
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
    ]
    
    timezone = forms.ChoiceField(
        choices=COUNTRY_TIMEZONES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )
    
    location = forms.ChoiceField(
        choices=LOCATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

    class Meta:
        model = UserProfile
        fields = ['timezone', 'email_notifications', 'web_notifications', 'bio', 'phone', 'location', 'avatar']
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500'
            }),
            'web_notifications': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Phone number'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white focus:outline-none focus:ring-2 focus:ring-blue-500',
                'accept': 'image/*'
            }),
        }


class UserUpdateForm(forms.ModelForm):
    """Form for updating user account information"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
        }

