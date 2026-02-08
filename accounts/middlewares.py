

from django.shortcuts import redirect
from rest_framework.permissions import SAFE_METHODS

# create a middalewares for jwt login required

ALLOWED_PATHS = [
    '/',
    'accounts/login',
    'work-profile',
    "company/companies"

]


class JwtCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if not request.user.is_authenticated and request.path not in ALLOWED_PATHS:

            if request.path == ALLOWED_PATHS[2] and request.method not in SAFE_METHODS:
                redirect("accounts:login_page")
                

            redirect("accounts:login_page")

        response = self.get_response(request)

        return response
