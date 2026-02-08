


from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter



app_name = "profile"

urlpatterns = [
    path("create_work_profile/<uuid:user_uuid>",
         views.CreateWorkProfile.as_view()),
    path("delete_work_profile/<uuid:user_uuid>/<str:company_name>",
         views.DeleteWorkProfileView.as_view())
]



router = SimpleRouter()
router.register(r'work-profile', views.WorkProfileView, basename='wprofile')

urlpatterns+=router.urls
