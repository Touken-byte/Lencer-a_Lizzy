from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailOUsernameBackend(ModelBackend):
    """Permite iniciar sesión con correo electrónico o con nombre de usuario"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('email')
        if username is None:
            return None

        try:
            if '@' in username:
                user = User.objects.get(email__iexact=username)
            else:
                user = User.objects.get(username__iexact=username)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None