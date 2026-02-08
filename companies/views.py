

from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.postgres.search import TrigramSimilarity
from django.http import QueryDict

from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse


from smtplib import SMTPException


from .models import Company, CompanyCheck
from . import serializers, paginators
from accounts.models import OtpCode


import logging
import utils
import datetime
import json

logging.basicConfig(filename="company.log", level=logging.INFO,
                    force=True, filemode="w+")


class CompanyViewset(ViewSet):

    permission_classes = [AllowAny]
    queryset = Company.objects.all()
    lookup_field = "company_name"

    def list(self, request):

        paginator = paginators.CompanyPaginator()

        paginate_qs = paginator.paginate_queryset(self.queryset, request)

        ser_data = serializers.CompanySerializer(paginate_qs, many=True)

        response = paginator.get_paginated_response(ser_data.data)
        response.status_code = status.HTTP_200_OK

        return response

    @extend_schema(
        summary="Give detail of the Company root and licsence",
    )
    
    def retrieve(self, request, pk=None):
        

        try:

            company = self.queryset.get(legal_name=pk)

            ser_data = serializers.CompanyDescSerializer(company)

        except Company.DoesNotExist:
            return Response({"message": "Does NOt Exist"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ser_data.data, status=status.HTTP_200_OK)


class CompanyCheckViewset(ViewSet):

    permission_classes = [IsAuthenticated,]

    def list(self, request):

        checking_companies = CompanyCheck.objects.filter(owner=request.user).order_by(
            "checked").only("name", "status", "checked", "name_uuid")

        query = request.query_params.get("search")

        if request.query_params.get("search"):

            checking_companies = checking_companies.annotate(
                similarity=TrigramSimilarity("name", query)).filter(similarity__gt=0.2).order_by("-similarity")

        ser_data = serializers.ShowCheckCompany(
            instance=checking_companies, many=True)

        return Response(ser_data.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):

        try:
            instance = CompanyCheck.objects.get(name_uuid=pk)

            ser_data = serializers.CheckingCompanySerializer(instance)

            return Response(ser_data.data, status=status.HTTP_200_OK)

        except CompanyCheck.DoesNotExist:

            return Response({"message": "Doesnt Exist"}, status=status.HTTP_404_NOT_FOUND)

        except ValidationError:

            return Response({"message": "Doesnt Exist"}, status=status.HTTP_404_NOT_FOUND)


class CompanyCheckRegisterView(APIView):
    permission_classes = [IsAuthenticated,]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):

        try:
            owner = get_user_model().objects.get(username=request.user.username)

        except get_user_model().DoesNotExist:

            return Response(status=status.HTTP_401_UNAUTHORIZED)

        ser_data = serializers.CheckingCompanySerializer(
            data=request.data, context={"request": request})
        ser_data.is_valid(raise_exception=True)
        instance = ser_data.create(ser_data.validated_data)

        try:
            utils.send_reminder_email(utils.random_admin(), instance.name)

        except SMTPException as err:
            logging.error(f"Email Error{err}")

        finally:
            return Response(ser_data.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        name_id = request.data
        if not name_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            CompanyCheck.objects.get(name_uuid=name_id).delete()
            return Response({"detail": "Deleted succesfully"}, status=status.HTTP_200_OK)

        except CompanyCheck.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class RegisterCompanyView(APIView):

    permission_classes = [IsAuthenticated,]

    def post(self, request, name_uuid):

        # Can Edit request.data
        if isinstance(request.data, QueryDict):
            request.data._mutable = True

        request.data["name_uuid"] = name_uuid

        ser_data = serializers.CompanySerializer(data=request.data)

        ser_data.is_valid(raise_exception=True)

        ser_data.save()

        return Response(ser_data.data, status=status.HTTP_200_OK)


class CheckCompanyEmailView(APIView):

    def post(self, request, company_email):

        code = utils.send_mail(company_email)
        expire = datetime.datetime.now()+datetime.timedelta(minutes=2)

        OtpCode.objects.create("companies app(check email)", code, expire)

        return Response(json.dumps(code), status=status.HTTP_200_OK)
