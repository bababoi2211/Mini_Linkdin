
from django.contrib import admin
from .models import Company, CompanyCheck


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):

    list_display = ("legal_name", "rating", "avg_salary", "registerd")

    fieldsets = [
        (
            "Company_license",
            {
                "fields": ('company_check',),
                "description": "This is the related foreign key for check company"
            }
        ),
        (
            "Basic Info",
            {
                "fields": ["legal_name", "rating", "members", "avg_salary", "avg_age", "registerd"]
            }
        ),

        (
            "locations",
            {
                "fields": ("locations", "coordinantes")
            }
        ),

    ]

    readonly_fields = ("registerd",)


admin.site.register(CompanyCheck)
