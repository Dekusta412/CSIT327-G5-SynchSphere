from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import SecurityQuestion, UserSecurityAnswer

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        error_messages = {
            "username": {
                "unique": "This username is already taken. Please choose another.",
            },
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254)

class SetSecurityQuestionsForm(forms.Form):
    question_1 = forms.ModelChoiceField(queryset=SecurityQuestion.objects.all(), empty_label="Select a question")
    answer_1 = forms.CharField(max_length=100)
    question_2 = forms.ModelChoiceField(queryset=SecurityQuestion.objects.all(), empty_label="Select a question")
    answer_2 = forms.CharField(max_length=100)
    question_3 = forms.ModelChoiceField(queryset=SecurityQuestion.objects.all(), empty_label="Select a question")
    answer_3 = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super().clean()
        q1 = cleaned_data.get("question_1")
        q2 = cleaned_data.get("question_2")
        q3 = cleaned_data.get("question_3")
        if q1 and q2 and q3:
            if q1 == q2 or q1 == q3 or q2 == q3:
                raise forms.ValidationError("You must select three unique security questions.")
        return cleaned_data

class RequestPasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("No user with that username.")
        return username

class AnswerSecurityQuestionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user_answers = kwargs.pop('user_answers')
        super().__init__(*args, **kwargs)
        for i, user_answer in enumerate(user_answers):
            self.fields[f'answer_{i+1}'] = forms.CharField(label=user_answer.question.question_text, max_length=100)

class ResetPasswordForm(SetPasswordForm):
    pass
