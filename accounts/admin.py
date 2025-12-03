from django.contrib import admin
from .models import SecurityQuestion, UserSecurityAnswer

def populate_security_questions(modeladmin, request, queryset):
    questions = [
        "What was your childhood nickname?",
        "In what city did you meet your spouse/significant other?",
        "What is the name of your favorite childhood friend?",
        "What street did you live on in third grade?",
        "What is your oldest sibling’s birthday month and year? (e.g., January 1900)",
        "What is the middle name of your youngest child?",
        "What is your oldest cousin's first and last name?",
        "What was the name of your first pet?",
        "In what city or town was your first job?",
        "What was the make and model of your first car?",
    ]
    for question_text in questions:
        SecurityQuestion.objects.get_or_create(question_text=question_text)

populate_security_questions.short_description = "Populate default security questions"

class SecurityQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text',)
    actions = [populate_security_questions]

admin.site.register(SecurityQuestion, SecurityQuestionAdmin)
admin.site.register(UserSecurityAnswer)