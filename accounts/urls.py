from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Password reset flow
    path("password_reset/", views.request_password_reset_view, name="request_password_reset"),
    path("password_reset/answers/", views.answer_security_questions_view, name="answer_security_questions"),
    path("password_reset/confirm/", views.reset_password_view, name="reset_password"),
]
