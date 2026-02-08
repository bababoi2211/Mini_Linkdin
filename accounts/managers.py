

from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    
    def create_user(self, username, phone_number, email, legal_name, password):

        if not username:
            raise ValueError('Must Have a username Field')

        if not phone_number:
            raise ValueError('Must Have a phone_number Field')

        if not email:
            raise ValueError('Must Have a email Field')

        if not legal_name:
            raise ValueError('Must Have a legal_name Field')

        user = self.model(username=username, phone_number=phone_number,
                          email=self.normalize_email(email), legal_name=legal_name)
        user.set_password(password)
        # user.is_admin = False
        user.save(using=self._db)

        return user

    def create_superuser(self, username, phone_number, email, legal_name, password, **extra_fields):

        user = self.create_user(username=username, phone_number=phone_number, email=self.normalize_email(
            email), legal_name=legal_name, password=password)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        user.is_admin = True
        user.save(using=self._db)

        return user
