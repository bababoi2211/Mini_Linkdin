
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db.models import Sum
from .managers import UserManager
import datetime
import pytz
import uuid


class User(AbstractBaseUser, PermissionsMixin):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(unique=True, max_length=20)
    phone_number = models.CharField(max_length=11, unique=True, validators=[])
    email = models.EmailField(unique=True)
    legal_name = models.CharField()
    has_job = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number', 'email', 'legal_name']

    objects = UserManager()

    def __str__(self):
        return f"{self.username}-{self.legal_name}"
        return f"{self.username}-{self.legal_name}"

    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True

        return self.is_staff

    def has_perm(self, perm, obj=None):
        if self.phone_number == '09912037758':
            return True

        return super().has_perm(perm, obj)

    @property
    def is_staff(self):

        return self.is_admin


# put unique together in the work span date time
class WorkProfile(models.Model):

    CATEGORY_CHOICES = {
        "En": "Engenering",
        "IT": "Tech",
        "DR": "Physics",
        "TE": "Teacher",
        "NE": "NO Category",

    }

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='profile')

    company = models.CharField(max_length=255, unique=True)
    job_category = models.CharField(
        max_length=255, choices=CATEGORY_CHOICES, default="NO category")
    job_title = models.CharField(max_length=255)
    rank = models.CharField(max_length=60, default='No Ranking')
    avg_hourly_incomes = models.DecimalField(
        max_digits=10, decimal_places=2, default=2.00)
    description = models.TextField()

    work_span_from = models.DateTimeField()
    work_span_till = models.DateTimeField()
    total_experience_months = models.PositiveIntegerField(default=0)

    def clean(self):
        super().clean()

        date_from = self.work_span_from
        correct_date = datetime.datetime.now(pytz.timezone(
            "Asia/Tehran")) - datetime.timedelta(days=1)

        if date_from >= correct_date:

            raise ValidationError('Work start date must be before today.')

        if (self.work_span_from and self.work_span_till) and self.work_span_from > self.work_span_till:
            raise ValidationError("The working time is incorrect")

        # choices field validation

        valid_choices = [choice[0] for choice in self.CATEGORY_CHOICES]
        if self.category and self.category not in valid_choices:
            pass

    def save(self, *args, **kwargs):
        self.total_experience_months = (
            self.work_span_till - self.work_span_from).days // 30
        # self.companies = self.objects.filter(id=self.id).count()

        super().save(*args, **kwargs)


class OtpCode(models.Model):
    title = models.CharField()
    code = models.CharField()
    created = models.DateTimeField(auto_now_add=True)
    expire = models.DateTimeField()

    def is_expired(self):
        return datetime.datetime.now() > self.expire


