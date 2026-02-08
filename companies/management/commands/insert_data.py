

from django.core.management.base import BaseCommand
from ...models import Company
from django.db import connection


datas = [
    ["Cuberneties", "IT", 22, "https://docs",
        {"postal_code": "21233221"}, 2.4, 18.00, 22],
    ["Netflix", "IT", 12, "https://ddocs",
        {"postal_code": "11233221"}, 3.4, 48.00, 22],
    ["Snapp", "IT", 22, "https://docs",
        {"postal_code": "21233221"}, 4.4, 28.00, 21],
    ["cuber", "IT", 22, "https://docs",
        {"postal_code": "21233221"}, 1.4, 12.00, 26],
    ["Uber", "IT", 22, "https://docs",
        {"postal_code": "21233221"}, 2.4, 13.00, 26],
]


class Command(BaseCommand):
    help = "Insert Data into"

    def handle(self, *args, **options):

        try:
            for data in datas:
                Company.objects.create(
                    name=data[0],
                    field=data[1],
                    members=data[2],
                    locations=data[3],
                    coordinantes=data[4],
                    rating=data[5],
                    avg_income=data[6],
                    avg_age=data[7]
                )

        except Exception as err:
            self.stdout.write(
                self.style.ERROR(err)
            )
            return
        self.stdout.write(
            self.style.SUCCESS("The Data Has Entered Succesfully")
        )
