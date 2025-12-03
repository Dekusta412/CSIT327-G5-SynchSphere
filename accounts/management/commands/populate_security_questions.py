from django.core.management.base import BaseCommand
from accounts.models import SecurityQuestion

class Command(BaseCommand):
    help = 'Populates the database with default security questions'

    def handle(self, *args, **options):
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
            _, created = SecurityQuestion.objects.get_or_create(question_text=question_text)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created question: "{question_text}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Question already exists: "{question_text}"'))
