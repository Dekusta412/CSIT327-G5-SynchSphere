from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from dashboard.models import UserProfile


class EditUserForm(forms.ModelForm):
    """Form for editing basic User fields"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white'}),
        }


class EditProfileForm(forms.ModelForm):
    """Form for editing extended profile fields (UserProfile)"""

    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'phone', 'location', 'timezone', 'email_notifications', 'web_notifications']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white', 'accept': 'image/*'}),
            'bio': forms.Textarea(attrs={'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white', 'rows': 4}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white'}),
            'location': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white'}),
            'timezone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded-lg bg-gray-700 border border-gray-600 text-white'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded'}),
            'web_notifications': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded'}),
        }

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