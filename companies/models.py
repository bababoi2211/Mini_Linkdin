

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model

import utils
import json


status = {
    "T": "Accepted",
    "F": "Denied",
    "NE": "checking"
}


class CompanyCheck(models.Model):
    name = models.CharField(unique=True)

    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="company_check_owner")

    name_uuid = models.UUIDField(unique=True)

    field = models.CharField()
    owner_eid = models.BigIntegerField()
    location = models.URLField()
    certificate = models.FileField(
        upload_to=f"certificate/{name}", validators=[FileExtensionValidator,], serialize=True)

    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=status, default="NE")
    checked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}-{self.status}"

    class Meta:
        ordering = ('checked', 'created')
        verbose_name_plural = 'companiesCheck'

    def __str__(self):
        return f"{self.name} |uuid:{self.name_uuid} "


# co = CompanyCheck.objects.first()
class Company(models.Model):

    company_check = models.OneToOneField(
        CompanyCheck, on_delete=models.CASCADE, related_name="check_company", default="dee")
    legal_name = models.CharField(unique=True)
    company_email = models.EmailField(unique=True, null=True, blank=True)
    members = models.IntegerField()
    locations = models.URLField()
    coordinantes = models.JSONField()
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=2.5)
    avg_salary = models.DecimalField(decimal_places=2, max_digits=5)
    avg_age = models.PositiveIntegerField(default=18, validators=[
                                          utils.legal_age_validator,])
    description = models.TextField(null=False)

    registerd = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-rating',)
        verbose_name_plural = "companies"

    def clean(self):

        if self.rating > 5 or self.rating <= 0:
            raise ValidationError(_("rating should be above 0 and below 5"))
