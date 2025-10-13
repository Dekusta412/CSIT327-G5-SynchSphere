from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import SignUpForm

try:
    from SynchSphere.realtime import publish_event
except Exception:
    def publish_event(event, data):
        # fallback noop if realtime module isn't available
        return

from django.conf import settings
from django.contrib.auth import views as auth_views


class CustomPasswordResetView(auth_views.PasswordResetView):
    """Use settings.DEFAULT_FROM_EMAIL (or EMAIL_USER) as the from address for reset emails."""
    # Templates are already set in urls, but ensure defaults exist
    email_template_name = "registration/password_reset_email.html"
    html_email_template_name = "registration/password_reset_email_html.html"
    subject_template_name = "registration/password_reset_subject.txt"

    def get_from_email(self):
        # Use DEFAULT_FROM_EMAIL if set, otherwise fallback to EMAIL_HOST_USER
        return getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)

    def get_email_options(self):
        # Ensure from_email is set when sending
        opts = super().get_email_options() or {}
        from_email = self.get_from_email()
        if from_email:
            opts['from_email'] = from_email
        return opts

def register_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            try:
                publish_event('user.registered', user.username)
            except Exception:
                pass
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "accounts/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully.")
            try:
                publish_event('user.logged_in', user.username)
            except Exception:
                pass
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    try:
        publish_event('user.logged_out', getattr(request.user, 'username', 'anonymous'))
    except Exception:
        pass
    # Redirect to the site home page after logout
    return redirect("home")