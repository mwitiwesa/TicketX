import os

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'

    def ready(self):
        if os.getenv('DEBUG', 'False').lower() != 'true':
            return

        email = os.getenv('DJANGO_SUPERUSER_EMAIL')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
        if not email or not password:
            return

        try:
            from django.contrib.auth import get_user_model
            from django.db.utils import OperationalError, ProgrammingError

            User = get_user_model()
            user = User.objects.filter(email=email).first()
            if user:
                user.role = 'ADMIN'
                user.is_main_admin = True
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.set_password(password)
                user.save()
                print(f'Updated superuser {email}')
            else:
                User.objects.create_superuser(email=email, password=password)
                print(f'Created superuser {email}')
        except (OperationalError, ProgrammingError) as exc:
            # Database might not be ready yet (migrations / first run), skip safely.
            print(f'Superuser creation skipped until DB is ready: {exc}')
        except Exception as exc:
            print(f'Superuser creation skipped: {exc}')