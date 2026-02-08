
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import CompanyCheck
from smtplib import SMTPException
import uuid
import utils


@receiver(pre_save, sender=CompanyCheck)
def my_handle(sender, instance, **kwargs):

    name = instance.name

    name_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, name)
    instance.name_uuid = name_uuid
    # instance.save()

    return instance


@receiver(post_save, sender=CompanyCheck)
def my_handle(sender, instance, **kwargs):
    if instance.checked == True and not kwargs["created"]:
        try:
            utils.send_reminder_email(
                instance.owner.email, f"Your company {instance.name} has been checked")

        except SMTPException as err:
            utils.send_reminder_email(
                "danialmajdzadde@gmail.cin", f"tell {instance.owenr.email} his company {instance.name} has been checked")

    return instance
