from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('CLIENT', 'Client'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CLIENT')
    is_main_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.email or self.username