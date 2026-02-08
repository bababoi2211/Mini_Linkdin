
import datetime
from django.core.management import BaseCommand
from ...models import OtpCode
import pytz


class Command(BaseCommand):

    help = "Remove all expired codes"

    def handle(self, *args, **options):
        now = datetime.datetime.now(tz=pytz.timezone("Asia/tehran"))

        expired_codes = OtpCode.objects.filter(expire__gt=now)
        expired_codes.delete()
        
        return self.stdout.write("Removed All Expired codes.")
