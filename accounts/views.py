
# GEt Chat GPT validation for this view


from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.db.models import Sum
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.contrib.auth import login


from rest_framework.response import Response
from rest_framework.views import APIView, View
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, SAFE_METHODS
from rest_framework.decorators import action
from rest_framework.decorators import permission_classes as permission_decorator

from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer


from rest_framework_simplejwt.views import TokenObtainSlidingView
from rest_framework_simplejwt.tokens import RefreshToken, BlacklistMixin
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


from pathlib import Path
from django.contrib.auth import get_user_model

from . import serializers, permissions, forms,paginators
from .models import WorkProfile as ProfileObj
import datetime
import json


class UserViewset(viewsets.ViewSet):
    permission_classes = [IsAdminUser,]
    querysets = get_user_model().objects.all()

    # def setup(self, request, *args, **kwargs):
    #     self._User = get_user_model()
    #     self.queryset = self._User.objects.all()
    #     return super().setup(request, *args, **kwargs)

    # if the user isnt authenticated it comes up with this messaege

    def get_authenticate_header(self, request):
        return 'Bearer realm="myapi"'

    def list(self, request):

        self.check_object_permissions(request,self.querysets)
        paginator = paginators.MyCursorPaginatior()
        paginated_qs = paginator.paginate_queryset(self.querysets, request)

        ser_data = serializers.UserSerializers(
            instance=paginated_qs, many=True)

        # ser_data.is_valid(raise_exception=True)
        response = paginator.get_paginated_response(ser_data.data)
        
        response.status_code = status.HTTP_200_OK

        has_next = response.data.get("previous") is not None
        has_previous = response.data.get("previous") is not None

        return response
        # return Response(data=ser_data.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):

        user = get_object_or_404(self.querysets, pk=pk)

        ser_data = serializers.UserSerializers(instance=user)

        # ser_data.is_valid(raise_exception=True)

        return Response(data=ser_data.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        user = get_object_or_404(self.querysets, pk=pk)
        username = user.username
        user.is_active = False
        user.save()
        return Response({"detail": f"user {username} Deactivated"}, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['get'], url_path='verify-jwt')
    def verify_user_jwt(self, request):
        self
        # self.get_authenticate_header(request)


class UserViewAll(APIView):
    permission_classes = [permissions.AuthInCookie, IsAuthenticated]
    throttle_classes = ''

    def get(self, request):

        user = get_user_model().objects.all()
        ser_data = serializers.UserSerializers(instance=user, many=True)

        return Response(data=ser_data.data, status=status.HTTP_200_OK)


class UserRegisteryView(APIView):

    metadata_class = permissions.CustomeMeta
    permission_classes = [permissions.NotAuthenticated,]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return JsonResponse({"message": "user is already signed in"}, status=status.HTTP_400_BAD_REQUEST)

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        ser_data = serializers.UserRegisterySerializer(data=request.data)

        ser_data.is_valid(raise_exception=True)

        try:

            user = ser_data.create(ser_data.validated_data)
            request.session['UUID'] = f"{user.id}"
            print(ser_data.validated_data)
            ser_user_data = serializers.UserSerializers(
                ser_data.validated_data)

            print(ser_user_data.data)
            response = Response(ser_user_data.data,
                                status=status.HTTP_201_CREATED)

            response.set_cookie(
                key='UUID',
                value=f"{user.id}",
                httponly=True,
                secure=True
            )

            return response

        except KeyboardInterrupt as err:
            print(err)
            ser_data.delete(request.data['username'])
            return Response({"message": "Error accoured"}, status=status.HTTP_400_BAD_REQUEST)

    def options(self, request, *args, **kwargs):

        return super().options(request, *args, **kwargs)


class UserLoginView(APIView):
    permission_classes = [permissions.NotAuthenticated,]

    def setup(self, request, *args, **kwargs):

        self._User = get_user_model()
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        ser_data = serializers.UserLoginSerializer(data=request.data)
        ser_data.is_valid(raise_exception=True)

        username = ser_data.validated_data.get("username")

        user = self._User.objects.filter(username=username).first()

        if not user:
            return Response({"message": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username,
                            password=ser_data.validated_data.get("password"))

        if user:
            token = RefreshToken.for_user(user)

            # We Use this in prod
            # return Response(
            #     {
            #         'refresh': str(token),
            #         'access': str(token.access_token)
            #     }
            # )

            refresh_token = str(token)
            access_token = str(token.access_token)

            response = Response({
                'refresh': refresh_token,
                'access': access_token
            }
            )

            # if request.COOKIES.get("access_token"):
            # Wont work because web servers like chrome and safari ignore the next set cookie after the removal

            #     response.delete_cookie('access_token')

            #     response.set_cookie(
            #         'access_token', value=access_token, httponly=True, secure=True)
            # else:
            # print("NO cookie")

            response.set_cookie(
                'session_id', value=user.id, httponly=True, secure=True)

            response.set_cookie(
                'access_token', value=access_token, httponly=True, secure=True)

            return response

        return Response({"message": "Authentication Problem"}, status=status.HTTP_400_BAD_REQUEST)


class UserLogOut(APIView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({"message": "No refresh token provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)

            token.blacklist()

            response = Response(
                {"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)

            response.delete_cookie('refresh_token')

            return response

        except InvalidToken as err:

            return Response({"message": str(err.add_note("Invalid token"))[:30]}, status=status.HTTP_400_BAD_REQUEST)

        except TokenError as err:
            return Response({"message": f"{str(err)}"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomeObtainPairView(TokenObtainSlidingView):
    serializer_class = serializers.CustomeObtainPairSerializer


class ShowTemplateView(APIView):

    renderer_classes = [TemplateHTMLRenderer,]

    def get(self, request, *args, **kwargs):
        users = get_user_model().objects.all()

        return Response({'users': users}, template_name='user.html')


class UserFormView(View):

    form_class = forms.UserLoginForm

    def get(self, request, *args, **kwargs):

        form = self.form_class()

        return render(request, "accounts/login.html", {"form": form})

    def post(self, request, *args, **kwargs):

        form = self.form_class(request.POST)

        if form.is_valid():
            cd = form.cleaned_data

            user = get_object_or_404(get_user_model(), username=cd["username"])

            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        return JsonResponse({"message": "logined Succesfully"})


# region Profile Views


# endregion
