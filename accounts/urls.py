

from django.urls import path, include
from rest_framework import routers

from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views


app_name = 'accounts'

token_urls = [
    path('create', views.CustomeObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify', TokenVerifyView.as_view(), name="verify_token")
]


urlpatterns = [
    path("all", views.UserViewAll.as_view()),
    path('create/user', views.UserRegisteryView.as_view(), name='user_registery'),
    path('login', views.UserLoginView.as_view(),name="login_page"),
    path('logout', views.UserLogOut.as_view()),
    path("login/form",views.UserFormView.as_view(),name="login_form"),
    
    path("token/", include(token_urls)),
    
    
    # path("show_template",views.ShowTemplateView.as_view(),name='user_template')
]


router = routers.SimpleRouter()
router.register(r'users', views.UserViewset, basename='users')
urlpatterns += router.urls
