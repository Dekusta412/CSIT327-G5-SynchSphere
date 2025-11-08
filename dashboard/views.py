from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q
from .models import Event, Reminder, Notification, UserProfile
from .forms import EventForm, ReminderForm, UserProfileForm, UserUpdateForm
from django.contrib.auth.forms import PasswordChangeForm
from .utils import get_user_profile, get_unread_count, invalidate_user_cache, get_timezone
from datetime import datetime, timedelta
import json
import pytz  # Still needed for UTC


@login_required
def dashboard_view(request):
    """Main dashboard page showing reminders and notifications"""
    user = request.user
    profile = get_user_profile(user)
    
    # Get upcoming reminders (next 7 days) - optimized query with select_related
    now = timezone.now()
    upcoming_reminders = Reminder.objects.filter(
        user=user,
        reminder_time__gte=now,
        reminder_time__lte=now + timedelta(days=7),
        is_sent=False
    ).order_by('reminder_time')[:10].only('id', 'title', 'reminder_time', 'is_sent')
    
    # Get recent notifications (unread first) - optimized query
    notifications = Notification.objects.filter(user=user).order_by('-is_read', '-created_at')[:10].only(
        'id', 'title', 'message', 'is_read', 'created_at', 'notification_type'
    )
    unread_count = get_unread_count(user)
    
    # Get upcoming events (next 7 days) - optimized query
    upcoming_events = Event.objects.filter(
        user=user,
        start_time__gte=now,
        start_time__lte=now + timedelta(days=7)
    ).order_by('start_time')[:5].only('id', 'title', 'start_time', 'end_time', 'location')
    
    context = {
        'upcoming_reminders': upcoming_reminders,
        'notifications': notifications,
        'unread_count': unread_count,
        'upcoming_events': upcoming_events,
        'profile': profile,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def calendar_view(request):
    """Calendar page with interactive calendar"""
    user = request.user
    profile = get_user_profile(user)
    
    # Get all events for the user - optimized query with limit for initial load
    events = Event.objects.filter(user=user).order_by('start_time').only(
        'id', 'title', 'start_time', 'end_time', 'description', 'location'
    )[:100]  # Limit to 100 events for initial load
    
    # Convert events to JSON for calendar - optimized timezone conversion
    user_tz = get_timezone(profile.timezone)
    events_data = []
    
    for event in events:
        # Convert UTC to user's timezone for display
        start_local = event.start_time.astimezone(user_tz)
        end_local = event.end_time.astimezone(user_tz)
        
        event_data = {
            'id': event.id,
            'title': event.title,
            'start': start_local.isoformat(),
            'end': end_local.isoformat(),
            'extendedProps': {
                'description': (event.description or '')[:200],  # Limit description length
                'location': event.location or '',
            },
        }
        events_data.append(event_data)
    
    unread_count = get_unread_count(user)
    
    context = {
        'events': events,
        'events_json': json.dumps(events_data),
        'events_list_data': json.dumps(events_data),  # Reuse same data
        'profile': profile,
        'unread_count': unread_count,
    }
    
    return render(request, 'dashboard/calendar.html', context)


@login_required
def timezone_conversion_view(request):
    """Timezone conversion page"""
    user = request.user
    profile = get_user_profile(user)
    
    # Get user's events - optimized query
    events = Event.objects.filter(user=user).order_by('start_time').only(
        'id', 'title', 'start_time', 'end_time', 'description', 'location'
    )
    
    # Get selected timezone from request or use profile default
    selected_tz = request.GET.get('timezone', profile.timezone)
    
    # Convert events to selected timezone - optimized
    selected_tz_obj = get_timezone(selected_tz)
    converted_events = [
        {
            'event': event,
            'start_converted': event.start_time.astimezone(selected_tz_obj),
            'end_converted': event.end_time.astimezone(selected_tz_obj),
            'timezone': selected_tz,
        }
        for event in events
    ]
    
    # Get country-based timezones (same as in UserProfileForm)
    from .forms import UserProfileForm
    country_timezones = UserProfileForm.COUNTRY_TIMEZONES
    
    unread_count = get_unread_count(user)
    
    context = {
        'events': converted_events,
        'selected_timezone': selected_tz,
        'all_timezones': [tz[0] for tz in country_timezones],
        'timezone_choices': country_timezones,
        'profile': profile,
        'unread_count': unread_count,
    }
    
    return render(request, 'dashboard/timezone_conversion.html', context)


@login_required
def notifications_view(request):
    """Notifications management page"""
    user = request.user
    profile = get_user_profile(user)
    
    # Get all notifications - optimized query
    notifications = Notification.objects.filter(user=user).order_by('-created_at').only(
        'id', 'title', 'message', 'notification_type', 'is_read', 'delivery_status', 'created_at'
    )
    
    # Mark as read if requested
    if request.method == 'POST' and 'mark_read' in request.POST:
        notification_id = request.POST.get('notification_id')
        if notification_id:
            notification = get_object_or_404(Notification, id=notification_id, user=user)
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            invalidate_user_cache(user.id)  # Clear cache
            messages.success(request, 'Notification marked as read.')
            return redirect('dashboard:notifications')
    
    # Toggle notification preferences
    if request.method == 'POST' and 'toggle_notifications' in request.POST:
        profile.email_notifications = not profile.email_notifications
        profile.save()
        invalidate_user_cache(user.id)  # Clear cache
        messages.success(request, f'Email notifications {"enabled" if profile.email_notifications else "disabled"}.')
        return redirect('dashboard:notifications')
    
    unread_count = get_unread_count(user)
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'profile': profile,
    }
    
    return render(request, 'dashboard/notifications.html', context)


@login_required
def settings_view(request):
    """Settings page for account management"""
    user = request.user
    profile = get_user_profile(user)
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=profile)
            user_form = UserUpdateForm(request.POST, instance=user)
            
            if profile_form.is_valid() and user_form.is_valid():
                profile_form.save()
                user_form.save()
                invalidate_user_cache(user.id)  # Clear cache
                messages.success(request, 'Profile updated successfully.')
                return redirect('dashboard:settings')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')
                return redirect('dashboard:settings')
        elif 'logout' in request.POST:
            from django.contrib.auth import logout
            logout(request)
            messages.info(request, 'You have been logged out.')
            return redirect('accounts:login')
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserUpdateForm(instance=user)
        password_form = PasswordChangeForm(user)
    
    unread_count = get_unread_count(user)
    
    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'password_form': password_form,
        'profile': profile,
        'unread_count': unread_count,
    }
    
    return render(request, 'dashboard/settings.html', context)


@login_required
def profile_view(request):
    """User profile page for viewing and editing profile"""
    user = request.user
    profile = get_user_profile(user)
    
    # Get stats for display - optimized queries
    total_events = Event.objects.filter(user=user).count()
    active_reminders = Reminder.objects.filter(user=user, is_sent=False).count()
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
            user_form = UserUpdateForm(request.POST, instance=user)
            
            if profile_form.is_valid() and user_form.is_valid():
                profile_form.save()
                user_form.save()
                invalidate_user_cache(user.id)  # Clear cache
                messages.success(request, 'Profile updated successfully.')
                return redirect('dashboard:profile')
        elif 'cancel' in request.POST:
            return redirect('dashboard:profile')
    else:
        profile_form = UserProfileForm(instance=profile)
        user_form = UserUpdateForm(instance=user)
    
    unread_count = get_unread_count(user)
    
    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'profile': profile,
        'unread_count': unread_count,
        'total_events': total_events,
        'active_reminders': active_reminders,
    }
    
    return render(request, 'dashboard/profile.html', context)


# API Views for Event Management
@login_required
@require_http_methods(["GET", "POST"])
def events_api(request):
    """API endpoint for getting and creating events"""
    if request.method == 'GET':
        # Get events for calendar
        start = request.GET.get('start')
        end = request.GET.get('end')
        
        events = Event.objects.filter(user=request.user)
        
        if start and end:
            events = events.filter(
                Q(start_time__gte=start) | Q(end_time__lte=end)
            )
        
        events_data = []
        profile = get_user_profile(request.user)
        user_tz = get_timezone(profile.timezone)
        
        for event in events:
            start_local = event.start_time.astimezone(user_tz)
            end_local = event.end_time.astimezone(user_tz)
            
            events_data.append({
                'id': event.id,
                'title': event.title,
                'start': start_local.isoformat(),
                'end': end_local.isoformat(),
                'description': event.description,
                'location': event.location,
            })
        
        return JsonResponse(events_data, safe=False)
    
    elif request.method == 'POST':
        # Create new event
        data = json.loads(request.body)
        form = EventForm(data)
        
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            # Convert local time to UTC
            profile = get_user_profile(request.user)
            user_tz = get_timezone(profile.timezone)
            event.start_time = user_tz.localize(datetime.fromisoformat(data['start_time'].replace('Z', ''))).astimezone(pytz.UTC)
            event.end_time = user_tz.localize(datetime.fromisoformat(data['end_time'].replace('Z', ''))).astimezone(pytz.UTC)
            event.save()
            return JsonResponse({'success': True, 'id': event.id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@login_required
@require_http_methods(["GET", "PUT", "DELETE"])
def event_detail_api(request, event_id):
    """API endpoint for getting, updating, or deleting a specific event"""
    event = get_object_or_404(Event, id=event_id, user=request.user)
    
    if request.method == 'GET':
        profile = get_user_profile(request.user)
        user_tz = get_timezone(profile.timezone)
        
        return JsonResponse({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'start_time': event.start_time.astimezone(user_tz).isoformat(),
            'end_time': event.end_time.astimezone(user_tz).isoformat(),
            'location': event.location,
        })
    
    elif request.method == 'PUT':
        data = json.loads(request.body)
        form = EventForm(data, instance=event)
        
        if form.is_valid():
            event = form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
    elif request.method == 'DELETE':
        event.delete()
        return JsonResponse({'success': True})


@login_required
def create_event_view(request):
    """View for creating a new event"""
    profile = get_user_profile(request.user)
    
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            # Convert local time to UTC
            user_tz = get_timezone(profile.timezone)
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            
            # If datetime is naive, localize it; if aware, convert to user_tz first then UTC
            if timezone.is_naive(start_time):
                event.start_time = user_tz.localize(start_time).astimezone(pytz.UTC)
            else:
                event.start_time = start_time.astimezone(pytz.UTC)
            
            if timezone.is_naive(end_time):
                event.end_time = user_tz.localize(end_time).astimezone(pytz.UTC)
            else:
                event.end_time = end_time.astimezone(pytz.UTC)
            
            event.save()
            invalidate_user_cache(request.user.id)  # Clear cache
            messages.success(request, 'Event created successfully.')
            return redirect('dashboard:calendar')
    else:
        form = EventForm()
    
    unread_count = get_unread_count(request.user)
    
    return render(request, 'dashboard/create_event.html', {
        'form': form,
        'profile': profile,
        'unread_count': unread_count,
    })


@login_required
def edit_event_view(request, event_id):
    """View for editing an event"""
    event = get_object_or_404(Event, id=event_id, user=request.user)
    profile = get_user_profile(request.user)
    user_tz = pytz.timezone(profile.timezone)
    
    # Convert UTC to user's timezone for form
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save(commit=False)
            # Convert to UTC
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            
            if timezone.is_naive(start_time):
                event.start_time = user_tz.localize(start_time).astimezone(pytz.UTC)
            else:
                event.start_time = start_time.astimezone(pytz.UTC)
            
            if timezone.is_naive(end_time):
                event.end_time = user_tz.localize(end_time).astimezone(pytz.UTC)
            else:
                event.end_time = end_time.astimezone(pytz.UTC)
            
            event.save()
            invalidate_user_cache(request.user.id)  # Clear cache
            messages.success(request, 'Event updated successfully.')
            return redirect('dashboard:calendar')
    else:
        # Convert UTC times to user's timezone for display
        form = EventForm(instance=event)
        start_local = event.start_time.astimezone(user_tz)
        end_local = event.end_time.astimezone(user_tz)
        # Format for datetime-local input
        form.initial['start_time'] = start_local.strftime('%Y-%m-%dT%H:%M')
        form.initial['end_time'] = end_local.strftime('%Y-%m-%dT%H:%M')
    
    unread_count = get_unread_count(request.user)
    
    return render(request, 'dashboard/edit_event.html', {
        'form': form,
        'event': event,
        'profile': profile,
        'unread_count': unread_count,
    })


@login_required
def delete_event_view(request, event_id):
    """View for deleting an event"""
    event = get_object_or_404(Event, id=event_id, user=request.user)
    profile = get_user_profile(request.user)
    user_tz = pytz.timezone(profile.timezone)
    
    # Convert times for display
    event.start_time_display = event.start_time.astimezone(user_tz)
    event.end_time_display = event.end_time.astimezone(user_tz)
    
    if request.method == 'POST':
        event.delete()
        invalidate_user_cache(request.user.id)  # Clear cache
        messages.success(request, 'Event deleted successfully.')
        return redirect('dashboard:calendar')
    
    unread_count = get_unread_count(request.user)
    
    return render(request, 'dashboard/delete_event.html', {
        'event': event,
        'profile': profile,
        'unread_count': unread_count,
    })


# API Views for Profile Management
@login_required
@require_http_methods(["GET", "PUT"])
def profile_api(request):
    """API endpoint for getting and updating user profile"""
    user = request.user
    profile = get_user_profile(user)
    
    if request.method == 'GET':
        # Return profile data as JSON
        profile_data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'timezone': profile.timezone,
            'email_notifications': profile.email_notifications,
            'web_notifications': profile.web_notifications,
            'bio': profile.bio,
            'phone': profile.phone,
            'location': profile.location,
            'avatar': profile.avatar.url if profile.avatar else None,
            'created_at': profile.created_at.isoformat() if profile.created_at else None,
            'updated_at': profile.updated_at.isoformat() if profile.updated_at else None,
        }
        return JsonResponse(profile_data)
    
    elif request.method == 'PUT':
        # Update profile
        try:
            data = json.loads(request.body)
            
            # Update user fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'email' in data:
                user.email = data['email']
            user.save()
            
            # Update profile fields
            if 'timezone' in data:
                profile.timezone = data['timezone']
            if 'email_notifications' in data:
                profile.email_notifications = data['email_notifications']
            if 'web_notifications' in data:
                profile.web_notifications = data['web_notifications']
            if 'bio' in data:
                profile.bio = data['bio']
            if 'phone' in data:
                profile.phone = data['phone']
            if 'location' in data:
                profile.location = data['location']
            profile.save()
            invalidate_user_cache(user.id)  # Clear cache
            
            return JsonResponse({'success': True, 'message': 'Profile updated successfully'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

