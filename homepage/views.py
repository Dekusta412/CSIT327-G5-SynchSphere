from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q
from .models import Event, Reminder, Notification, UserProfile
from .forms import EventForm, ReminderForm, UserProfileForm, UserUpdateForm, CustomPasswordChangeForm
from accounts.forms import SetSecurityQuestionsForm
from accounts.models import UserSecurityAnswer
from .utils import (
    get_user_profile,
    get_unread_count,
    invalidate_user_cache,
    get_timezone,
    convert_to_utc,
)
from datetime import datetime, timedelta
import json
import pytz  # Still needed for UTC
import uuid


@login_required
def dashboard_view(request):
    """Main dashboard page showing reminders and notifications"""
    user = request.user
    profile = get_user_profile(user)
    
    # Get events happening within the next 24 hours (today's events)
    now = timezone.now()
    next_24_hours = now + timedelta(hours=24)
    
    # Get events within next 24 hours for today's events section
    upcoming_reminders = Event.objects.filter(
        user=user,
        start_time__gte=now,
        start_time__lte=next_24_hours
    ).order_by('start_time')[:10].only('id', 'title', 'start_time', 'location')
    
    # Get ALL notifications (unread first) for upcoming events section
    notifications = Notification.objects.filter(user=user).order_by('-is_read', '-created_at')[:10].only(
        'id', 'title', 'message', 'is_read', 'created_at', 'notification_type'
    )
    unread_count = get_unread_count(user)
    
    # Get upcoming events (next 7 days) for the events widget
    upcoming_events_qs = Event.objects.filter(
        user=user,
        start_time__gte=now,
        start_time__lte=now + timedelta(days=7)
    ).order_by('start_time')[:5].only('id', 'title', 'start_time', 'end_time', 'location')
    upcoming_events = list(upcoming_events_qs)
    upcoming_events_payload = [
        {
            'id': event.id,
            'title': event.title,
            'description': '',
            'start': event.start_time.astimezone(pytz.UTC).isoformat(),
            'end': event.end_time.astimezone(pytz.UTC).isoformat(),
            'location': event.location or '',
        }
        for event in upcoming_events
    ]
    
    context = {
        'upcoming_reminders': upcoming_reminders,
        'notifications': notifications,
        'unread_count': unread_count,
        'upcoming_events': upcoming_events,
        'upcoming_events_json': json.dumps(upcoming_events_payload),
        'has_upcoming_events': bool(upcoming_events_payload),
        'profile': profile,
        'profile_timezone': profile.timezone,
    }
    
    return render(request, 'homepage/dashboard.html', context)


@login_required
def calendar_view(request):
    """Calendar page with interactive calendar"""
    user = request.user
    profile = get_user_profile(user)
    
    # Get all events for the user - optimized query with limit for initial load
    events = Event.objects.filter(user=user).order_by('start_time').only(
        'id', 'title', 'start_time', 'end_time', 'description', 'location'
    )[:100]  # Limit to 100 events for initial load
    # Prepare display-friendly datetimes for server-rendered lists (converted to user's timezone)
    try:
        user_tz = get_timezone(profile.timezone)
        for ev in events:
            ev.start_time_display = ev.start_time.astimezone(user_tz)
            ev.end_time_display = ev.end_time.astimezone(user_tz)
    except Exception:
        # Fallback: leave original datetimes if timezone conversion fails
        pass
    
    # Send event datetimes to the client in UTC ISO format (with offset)
    # The browser/FullCalendar will display them in the user's local timezone.
    events_data = []

    for event in events:
        # Convert stored UTC datetimes to explicit UTC ISO strings
        start_utc = event.start_time.astimezone(pytz.UTC)
        end_utc = event.end_time.astimezone(pytz.UTC)

        event_data = {
            'id': event.id,
            'title': event.title,
            'start': start_utc.isoformat(),
            'end': end_utc.isoformat(),
            'extendedProps': {
                'description': (event.description or '')[:200],
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
    
    return render(request, 'homepage/calendar.html', context)


@login_required
def timezone_conversion_view(request):
    """Interactive timezone conversion dashboard powered by client-side formatting."""
    user = request.user
    profile = get_user_profile(user)
    
    events = Event.objects.filter(user=user).order_by('start_time').only(
        'id', 'title', 'start_time', 'end_time', 'description', 'location'
    )
    
    from .forms import UserProfileForm
    timezone_choices = UserProfileForm.COUNTRY_TIMEZONES
    timezone_label_map = dict(timezone_choices)
    
    requested_tz = request.GET.get('timezone') or profile.timezone
    if requested_tz not in timezone_label_map:
        requested_tz = profile.timezone
    
    def offset_label_for_tz(tz_name: str) -> str:
        tz_obj = get_timezone(tz_name)
        now_local = timezone.now().astimezone(tz_obj)
        offset = now_local.utcoffset()
        if not offset:
            return "GMT"
        total_minutes = int(offset.total_seconds() // 60)
        sign = '+' if total_minutes >= 0 else '-'
        hours, minutes = divmod(abs(total_minutes), 60)
        return f"GMT{sign}{hours:02d}:{minutes:02d}"
    
    events_payload = [
        {
            'id': event.id,
            'title': event.title,
            'description': event.description or '',
            'start': event.start_time.astimezone(pytz.UTC).isoformat(),
            'end': event.end_time.astimezone(pytz.UTC).isoformat(),
            'location': event.location or '',
        }
        for event in events
    ]
    
    unread_count = get_unread_count(user)
    
    context = {
        'events': events,
        'events_json': json.dumps(events_payload),
        'has_events': bool(events_payload),
        'timezone_choices': timezone_choices,
        'timezone_meta_json': json.dumps(timezone_label_map),
        'default_timezone': requested_tz,
        'default_timezone_label': timezone_label_map.get(requested_tz, requested_tz),
        'default_timezone_offset': offset_label_for_tz(requested_tz),
        'profile_timezone': profile.timezone,
        'profile_timezone_label': timezone_label_map.get(profile.timezone, profile.timezone),
        'profile_timezone_offset': offset_label_for_tz(profile.timezone),
        'profile': profile,
        'unread_count': unread_count,
    }
    
    return render(request, 'homepage/timezone_conversion.html', context)


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
            return redirect('homepage:notifications')
    
    # Toggle notification preferences
    if request.method == 'POST' and 'toggle_notifications' in request.POST:
        profile.email_notifications = not profile.email_notifications
        profile.save()
        invalidate_user_cache(user.id)  # Clear cache
        messages.success(request, f'Email notifications {"enabled" if profile.email_notifications else "disabled"}.')
        return redirect('homepage:notifications')
    
    unread_count = get_unread_count(user)
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'profile': profile,
    }
    
    return render(request, 'homepage/notifications.html', context)


@login_required
def settings_view(request):
    """Settings page for account management"""
    user = request.user
    profile = get_user_profile(user)
    
    # Initialize forms (will be overridden if POST)
    profile_form = UserProfileForm(instance=profile)
    user_form = UserUpdateForm(instance=user)
    password_form = CustomPasswordChangeForm(user)
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=profile)
            user_form = UserUpdateForm(request.POST, instance=user)
            
            if profile_form.is_valid() and user_form.is_valid():
                profile_form.save()
                user_form.save()
                invalidate_user_cache(user.id)  # Clear cache
                messages.success(request, 'Profile updated successfully.')
                return redirect('homepage:settings')
        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                updated_user = password_form.save()
                update_session_auth_hash(request, updated_user)
                messages.success(request, 'Password changed successfully.')
                return redirect('homepage:settings')
            else:
                # Form is invalid, show errors - other forms stay initialized
                messages.error(request, 'Please correct the errors below.')
        elif 'logout' in request.POST:
            from django.contrib.auth import logout
            logout(request)
            messages.info(request, 'You have been logged out.')
            return redirect('accounts:login')
    
    unread_count = get_unread_count(user)
    
    context = {
        'profile_form': profile_form,
        'user_form': user_form,
        'password_form': password_form,
        'profile': profile,
        'unread_count': unread_count,
    }
    
    return render(request, 'homepage/settings.html', context)


@login_required
def set_security_questions_view(request):
    user = request.user
    if request.method == 'POST':
        form = SetSecurityQuestionsForm(request.POST)
        if form.is_valid():
            # Delete old answers
            UserSecurityAnswer.objects.filter(user=user).delete()
            
            # Create new answers
            q1 = form.cleaned_data['question_1']
            a1 = form.cleaned_data['answer_1']
            q2 = form.cleaned_data['question_2']
            a2 = form.cleaned_data['answer_2']
            q3 = form.cleaned_data['question_3']
            a3 = form.cleaned_data['answer_3']

            ans1 = UserSecurityAnswer(user=user, question=q1)
            ans1.set_answer(a1)
            ans1.save()

            ans2 = UserSecurityAnswer(user=user, question=q2)
            ans2.set_answer(a2)
            ans2.save()

            ans3 = UserSecurityAnswer(user=user, question=q3)
            ans3.set_answer(a3)
            ans3.save()
            
            messages.success(request, 'Your security questions have been set.')
            return redirect('homepage:settings')
    else:
        form = SetSecurityQuestionsForm()
        
    return render(request, 'homepage/set_security_questions.html', {'form': form})


@login_required
def profile_view(request):
    """Mobile-inspired profile dashboard with live stats and avatar editing."""
    user = request.user
    profile = get_user_profile(user)

    from .forms import UserProfileForm, UserUpdateForm

    total_events = Event.objects.filter(user=user).count()
    active_reminders = Reminder.objects.filter(user=user, is_sent=False).count()

    profile_form = UserProfileForm(instance=profile)
    user_form = UserUpdateForm(instance=user)
    save_success = False

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserUpdateForm(request.POST, instance=user)

        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            invalidate_user_cache(user.id)
            messages.success(request, 'Profile updated successfully.')
            save_success = True
            return redirect('homepage:profile')
        else:
            messages.error(request, 'Please fix the errors below.')

    unread_count = get_unread_count(user)
    recent_events = Event.objects.filter(user=user).order_by('-start_time')[:3]
    recent_reminders = Reminder.objects.filter(user=user).order_by('-reminder_time')[:3]

    context = {
        'profile': profile,
        'profile_form': profile_form,
        'user_form': user_form,
        'recent_events': recent_events,
        'recent_reminders': recent_reminders,
        'total_events': total_events,
        'active_reminders': active_reminders,
        'unread_count': unread_count,
        'save_success': save_success,
    }

    return render(request, 'homepage/profile.html', context)


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
            try:
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                if timezone.is_naive(start_dt):
                    start_dt = timezone.make_aware(start_dt, pytz.UTC)
                if timezone.is_naive(end_dt):
                    end_dt = timezone.make_aware(end_dt, pytz.UTC)
                events = events.filter(start_time__lte=end_dt, end_time__gte=start_dt)
            except Exception:
                pass
        
        events_data = []
        profile = get_user_profile(request.user)
        user_tz = get_timezone(profile.timezone)
        
        for event in events:
            # Send UTC ISO timestamps to the client for consistent parsing
            events_data.append({
                'id': event.id,
                'title': event.title,
                'start': event.start_time.astimezone(pytz.UTC).isoformat(),
                'end': event.end_time.astimezone(pytz.UTC).isoformat(),
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
            profile = get_user_profile(request.user)
            client_tz = data.get('client_tz')
            tz_name = client_tz or profile.timezone
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            event.start_time = convert_to_utc(start_time, tz_name, treat_input_as_local=bool(client_tz))
            event.end_time = convert_to_utc(end_time, tz_name, treat_input_as_local=bool(client_tz))
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
        # Return UTC ISO timestamps; client will convert/display in browser timezone
        return JsonResponse({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'start_time': event.start_time.astimezone(pytz.UTC).isoformat(),
            'end_time': event.end_time.astimezone(pytz.UTC).isoformat(),
            'location': event.location,
        })
    
    elif request.method == 'PUT':
        data = json.loads(request.body)
        form = EventForm(data, instance=event)

        if form.is_valid():
            updated = form.save(commit=False)
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            profile = get_user_profile(request.user)
            client_tz = data.get('client_tz')
            tz_name = client_tz or profile.timezone

            updated.start_time = convert_to_utc(start_time, tz_name, treat_input_as_local=bool(client_tz))
            updated.end_time = convert_to_utc(end_time, tz_name, treat_input_as_local=bool(client_tz))
            updated.save()
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
            client_tz = request.POST.get('client_tz') or profile.timezone
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            
            event.start_time = convert_to_utc(start_time, client_tz, treat_input_as_local=True)
            event.end_time = convert_to_utc(end_time, client_tz, treat_input_as_local=True)
            
            # Get invitation link from form (generated by JavaScript)
            invitation_link = request.POST.get('invitation_link', '')
            if invitation_link:
                event.invitation_link = invitation_link
            
            event.save()
            invalidate_user_cache(request.user.id)  # Clear cache
            messages.success(request, 'Event created successfully.')
            return redirect('homepage:calendar')
    else:
        form = EventForm()
        # Prefill from calendar interactions
        try:
            user_tz = get_timezone(profile.timezone)
            date_str = request.GET.get('date')
            start_param = request.GET.get('start')
            end_param = request.GET.get('end')
            start_local = None
            end_local = None
            if start_param:
                start_dt = datetime.fromisoformat(start_param.replace('Z', '+00:00'))
                if timezone.is_naive(start_dt):
                    start_dt = timezone.make_aware(start_dt, pytz.UTC)
                start_local = start_dt.astimezone(user_tz)
                if end_param:
                    end_dt = datetime.fromisoformat(end_param.replace('Z', '+00:00'))
                    if timezone.is_naive(end_dt):
                        end_dt = timezone.make_aware(end_dt, pytz.UTC)
                    end_local = end_dt.astimezone(user_tz)
                else:
                    end_local = start_local + timedelta(hours=1)
            elif date_str:
                # Default to 09:00 local time and 1-hour duration
                try:
                    base = datetime.strptime(date_str, '%Y-%m-%d')
                except Exception:
                    base = timezone.now().astimezone(user_tz)
                start_local = base.replace(hour=9, minute=0, second=0, microsecond=0)
                end_local = start_local + timedelta(hours=1)
            else:
                # Fallback: current local hour rounded
                now_local = timezone.now().astimezone(user_tz)
                start_local = now_local.replace(minute=0, second=0, microsecond=0)
                end_local = start_local + timedelta(hours=1)
            if start_local and end_local:
                form.initial['start_time'] = start_local.strftime('%Y-%m-%dT%H:%M')
                form.initial['end_time'] = end_local.strftime('%Y-%m-%dT%H:%M')
        except Exception:
            pass
    
    unread_count = get_unread_count(request.user)
    
    return render(request, 'homepage/create_event.html', {
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
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            client_tz = request.POST.get('client_tz') or profile.timezone
            
            event.start_time = convert_to_utc(start_time, client_tz, treat_input_as_local=True)
            event.end_time = convert_to_utc(end_time, client_tz, treat_input_as_local=True)
            
            # Get invitation link from form (generated/regenerated by JavaScript)
            invitation_link = request.POST.get('invitation_link', '')
            if invitation_link:
                event.invitation_link = invitation_link
            
            event.save()
            invalidate_user_cache(request.user.id)  # Clear cache
            messages.success(request, 'Event updated successfully.')
            return redirect('homepage:calendar')
    else:
        # Convert UTC times to user's timezone for display
        form = EventForm(instance=event)
        start_local = event.start_time.astimezone(user_tz)
        end_local = event.end_time.astimezone(user_tz)
        # Format for datetime-local input
        form.initial['start_time'] = start_local.strftime('%Y-%m-%dT%H:%M')
        form.initial['end_time'] = end_local.strftime('%Y-%m-%dT%H:%M')
    
    unread_count = get_unread_count(request.user)
    
    return render(request, 'homepage/edit_event.html', {
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
        return redirect('homepage:calendar')
    
    unread_count = get_unread_count(request.user)
    
    return render(request, 'homepage/delete_event.html', {
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


@login_required
@require_http_methods(["GET"])
def search_users_api(request):
    """API endpoint to search for registered users"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'users': []})
    
    # Search by username or email
    from django.contrib.auth.models import User
    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(email__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).exclude(id=request.user.id)[:10]  # Exclude current user, limit to 10 results
    
    users_data = []
    for user in users:
        full_name = f"{user.first_name} {user.last_name}".strip()
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': full_name if full_name else None,
        })
    
    return JsonResponse({'users': users_data})


@login_required
def meeting_invitation_view(request, token, event_id=None):
    """View for meeting invitation links"""
    # If event_id is provided in URL, use it; otherwise extract from invitation_link field
    if event_id:
        event = get_object_or_404(Event, id=event_id)
    else:
        # Try to find event by invitation link token
        invitation_link_pattern = f"/dashboard/meeting/{token}"
        event = Event.objects.filter(invitation_link__contains=invitation_link_pattern).first()
        if not event:
            messages.error(request, 'Invalid or expired meeting invitation link.')
            return redirect('homepage:calendar')
    
    profile = get_user_profile(request.user)
    user_tz = pytz.timezone(profile.timezone)
    
    # Convert event times to user's timezone
    start_local = event.start_time.astimezone(user_tz)
    end_local = event.end_time.astimezone(user_tz)
    
    # Check if user is the organizer or invited participant
    is_organizer = event.user == request.user
    is_invited = request.user.email in event.invite_participants if event.invite_participants else False
    
    unread_count = get_unread_count(request.user)
    
    context = {
        'event': event,
        'start_local': start_local,
        'end_local': end_local,
        'is_organizer': is_organizer,
        'is_invited': is_invited,
        'profile': profile,
        'unread_count': unread_count,
    }
    
    return render(request, 'homepage/meeting_invitation.html', context)


@login_required
@require_http_methods(["POST"])
def join_event_view(request):
    """Handle joining an event via invitation link"""
    try:
        data = json.loads(request.body)
        event_token = data.get('event_token')
        
        if not event_token:
            return JsonResponse({'success': False, 'error': 'Event token is required'}, status=400)
        
        # Find the event by invitation token
        event = Event.objects.filter(invitation_link__contains=event_token).first()
        
        if not event:
            return JsonResponse({'success': False, 'error': 'Event not found or link is invalid'}, status=404)
        
        # Check if the event has already passed
        if event.end_time < timezone.now():
            return JsonResponse({'success': False, 'error': 'This event has already ended'}, status=400)
        
        # Create a copy of the event for the user's calendar
        new_event = Event.objects.create(
            title=f"{event.title} (Joined)",
            description=event.description,
            start_time=event.start_time,
            end_time=event.end_time,
            location=event.location,
            user=request.user,
            external_calendar_id=str(event.id),  # Reference to original event
            external_calendar_type='joined'
        )
        
        # Create a notification
        Notification.objects.create(
            user=request.user,
            title='Event Added to Calendar',
            message=f'You have successfully joined "{event.title}"',
            notification_type='event',
            event=new_event
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Event has been added to your calendar',
            'event_id': new_event.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

