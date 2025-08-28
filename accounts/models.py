from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
        help_text="Upload a profile picture",
    )
    bio = models.TextField(
        max_length=500, blank=True, help_text="Brief description about yourself"
    )
    github_username = models.CharField(
        max_length=100, blank=True, help_text="Your GitHub username"
    )
    role = models.CharField(
        max_length=50,
        choices=[
            ("developer", "Developer"),
            ("manager", "Project Manager"),
            ("tester", "Tester"),
            ("designer", "Designer"),
            ("analyst", "Business Analyst"),
        ],
        default="developer",
        help_text="Your primary role in development projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
