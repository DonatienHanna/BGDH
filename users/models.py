# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Extension du modèle User standard avec des champs spécifiques au trading"""
    is_premium = models.BooleanField(default=False)
    risk_profile = models.CharField(max_length=20, choices=[
        ('conservative', 'Conservative'),
        ('moderate', 'Moderate'),
        ('aggressive', 'Aggressive'),
    ], default='moderate')
    notification_email = models.BooleanField(default=True)
    notification_push = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username