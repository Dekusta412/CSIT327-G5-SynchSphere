from django.db import models
from django.contrib.auth.models import User
import bcrypt

class SecurityQuestion(models.Model):
    question_text = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.question_text

class UserSecurityAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(SecurityQuestion, on_delete=models.CASCADE)
    answer_hash = models.CharField(max_length=128)

    def set_answer(self, raw_answer):
        self.answer_hash = bcrypt.hashpw(raw_answer.lower().encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_answer(self, raw_answer):
        return bcrypt.checkpw(raw_answer.lower().encode('utf-8'), self.answer_hash.encode('utf-8'))

    class Meta:
        unique_together = ('user', 'question')