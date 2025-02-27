from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from config.django_config import USERS


class Command(BaseCommand):
    help = "Create multiple users"

    def handle(self, *args, **kwargs):
        users_data = USERS

        for user_data in users_data:
            user = User.objects.create_user(
                username=user_data["username"],
                password=user_data["password"],
            )
            self.stdout.write(f"User {user.username} created")
