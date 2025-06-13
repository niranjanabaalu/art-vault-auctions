from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Rehashes the password for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')
        parser.add_argument('password', type=str, help='New password')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        password = kwargs['password']

        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Password updated for user '{username}'"))
        except User.DoesNotExist:
            self.stderr.write(f"User '{username}' does not exist.")
