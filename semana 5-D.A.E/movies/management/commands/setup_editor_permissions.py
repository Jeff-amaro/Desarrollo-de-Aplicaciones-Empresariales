"""Create the editores group and its restricted user."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction

GROUP_NAME = 'editores'
DEFAULT_USERNAME = 'editor'
DEFAULT_EMAIL = 'editor@dae.local'
DEFAULT_PASSWORD = 'Editor12345'

# The group can create and update movies but is not allowed to delete them.
MOVIE_PERMISSION_CODENAMES = ('add_movie', 'change_movie')


class Command(BaseCommand):
    help = (
        'Creates the "editores" group with add and change permissions for '
        'movies (without delete) and a user that belongs to it.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--username', default=DEFAULT_USERNAME)
        parser.add_argument('--email', default=DEFAULT_EMAIL)
        parser.add_argument('--password', default=DEFAULT_PASSWORD)

    @transaction.atomic
    def handle(self, *args, **options):
        group, group_created = self._get_or_create_group()
        user, user_created = self._get_or_create_user(
            options['username'],
            options['email'],
            options['password'],
        )
        user.groups.add(group)

        self.stdout.write(
            self.style.SUCCESS(
                f'Group "{GROUP_NAME}" '
                f'{"created" if group_created else "updated"} with '
                f'{len(MOVIE_PERMISSION_CODENAMES)} movie permissions.'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'User "{user.username}" '
                f'{"created" if user_created else "updated"} and added to '
                f'the "{GROUP_NAME}" group.'
            )
        )

    def _get_or_create_group(self):
        group, created = Group.objects.get_or_create(name=GROUP_NAME)
        permissions = Permission.objects.filter(
            content_type__app_label='movies',
            codename__in=MOVIE_PERMISSION_CODENAMES,
        )
        group.permissions.set(permissions)
        return group, created

    def _get_or_create_user(self, username, email, password):
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username=username,
            defaults={'email': email},
        )
        # Staff status is required to sign in to the Django admin site.
        update_fields = []
        if not user.is_staff:
            user.is_staff = True
            update_fields.append('is_staff')
        if created:
            user.set_password(password)
            update_fields.append('password')
        if update_fields:
            user.save(update_fields=update_fields)
        return user, created
