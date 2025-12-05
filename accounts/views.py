from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import SignUpForm, RequestPasswordResetForm, AnswerSecurityQuestionsForm, ResetPasswordForm
from .models import UserSecurityAnswer
from django.urls import reverse

try:
    from SynchSphere.realtime import publish_event
except Exception:
    def publish_event(event, data):
        # fallback noop if realtime module isn't available
        return

from django.conf import settings
from django.contrib.auth import views as auth_views


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
            return redirect("homepage:dashboard")
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
            return redirect("homepage:dashboard")
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

def request_password_reset_view(request):
    if request.method == 'POST':
        form = RequestPasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            User = get_user_model()
            user = User.objects.get(username=username)
            
            # Check if user has security questions
            if not UserSecurityAnswer.objects.filter(user=user).exists():
                messages.error(request, "You have not set up security questions. Please contact an administrator.")
                return redirect('accounts:request_password_reset')

            request.session['password_reset_username'] = username
            return redirect(reverse('accounts:answer_security_questions'))
    else:
        form = RequestPasswordResetForm()
    return render(request, 'accounts/request_password_reset.html', {'form': form})

def answer_security_questions_view(request):
    username = request.session.get('password_reset_username')
    if not username:
        return redirect('accounts:request_password_reset')

    User = get_user_model()
    user = get_object_or_404(User, username=username)
    user_answers = UserSecurityAnswer.objects.filter(user=user)

    if request.method == 'POST':
        form = AnswerSecurityQuestionsForm(request.POST, user_answers=user_answers)
        if form.is_valid():
            correct = True
            for i, user_answer in enumerate(user_answers):
                if not user_answer.check_answer(form.cleaned_data[f'answer_{i+1}']):
                    correct = False
                    break
            
            if correct:
                request.session['password_reset_verified'] = True
                return redirect(reverse('accounts:reset_password'))
            else:
                messages.error(request, "One or more answers were incorrect.")
    else:
        form = AnswerSecurityQuestionsForm(user_answers=user_answers)
    
    return render(request, 'accounts/answer_security_questions.html', {'form': form})

def reset_password_view(request):
    username = request.session.get('password_reset_username')
    verified = request.session.get('password_reset_verified')

    if not username or not verified:
        return redirect('accounts:request_password_reset')

    User = get_user_model()
    user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        form = ResetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            # Clean up session
            del request.session['password_reset_username']
            del request.session['password_reset_verified']
            messages.success(request, "Your password has been reset. You can now log in.")
            return redirect('accounts:login')
    else:
        form = ResetPasswordForm(user)

    return render(request, 'accounts/reset_password.html', {'form': form})

