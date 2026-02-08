

from django.urls import path, re_path
from rest_framework.routers import SimpleRouter

from . import views


app_name = "company"

urlpatterns = [
    path("register/", views.CompanyCheckRegisterView.as_view(),
         name="register_check_company"),
    path("Register/company/<uuid:name_uuid>/",
         views.RegisterCompanyView.as_view(), name="register_company"),
    path("Register/company/check-email/<str:company_email>",
         views.CheckCompanyEmailView.as_view(), name="check_company_email")
]


router = SimpleRouter()

router.register("", views.CompanyViewset, basename="company")
router.register("company-check", views.CompanyCheckViewset,
                basename="company_check")


urlpatterns += router.urls
