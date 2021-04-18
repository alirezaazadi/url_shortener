from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):

        if username or email:
            user_lookup_dict = {'username__iexact': username} if username else {'email__iexact': email}

            user_model = get_user_model()

            try:
                user = user_model._default_manager.get(**user_lookup_dict)  # noqa
            except user_model.DoesNotExist:
                pass
            else:
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user

        return None
