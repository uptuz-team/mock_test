from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.exceptions import ValidationError



class User(AbstractUser):
    ROLES = (
        ('pupil', 'Oʻquvchi'),
        ('teacher', 'Oʻqituvchi'),
        ('developer', 'Dasturchi'),
    )
    role = models.CharField(max_length=10, choices=ROLES)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    def save(self, *args, **kwargs):
        """ Agar user roli 'developer' bo'lsa, uni superuser va staff qiladi """
        if self.role == 'developer':
            self.is_superuser = True
            self.is_staff = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    
    