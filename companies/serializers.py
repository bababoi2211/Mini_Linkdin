
from rest_framework import serializers
from django.core.validators import URLValidator
from .models import Company, CompanyCheck
import re
import utils
from smtplib import SMTPException
import json
import uuid


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = "__all__"


class CheckingCompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanyCheck
        exclude = ("created", "checked", "owner")

        extra_kwargs = {
            "status": {"write_only": True},
            "name_uuid": {"read_only": True},
            "owner_eid": {"write_only": True},

            "certificate": {"write_only": True},
            "location": {"validators": [URLValidator,]}


        }

    def validate_owner_eid(self, value):

        # if len(value) > 15:
        #     raise serializers.ValidationError("The Lenght is more than 15")

        if not re.fullmatch(r"^\d{15}$", str(value)):
            raise serializers.ValidationError("INccorect EID")
        return value

    def validate_certificate(self, file):

        max_size = 2 * 1024 * 1024

        if file.size > max_size:
            raise serializers.ValidationError(
                "The File size cant be more than 2MB")
        return file

    def create(self, validated_data):

        validated_data["owner"] = self.context["request"].user

        return super().create(validated_data)


class ShowCheckCompany(serializers.Serializer):

    name = serializers.CharField()
    name_uuid = serializers.UUIDField()
    status = serializers.CharField()
    checked = serializers.BooleanField()

    def validate_name_uuid(self, name_uuid):
        pass


class CompanySerializer(serializers.ModelSerializer):

    # company_check = serializers.PrimaryKeyRelatedField(read_only=True)
    # company_check = CompanySerializer()
    name_uuid = serializers.UUIDField(write_only=True)

    class Meta:

        model = Company
        exclude = ("registerd", "company_check")

        # include = ("legal_name", "members", "locations", "coordinantes",
        #            "rating", "avg_salary", "avg_age", "description")

    def validate_rating(self, rating):
        if rating < 0 or rating > 5:
            raise serializers.ValidationError("Rating is incorrect")

        return rating

    def create(self, validated_data):
        name_uuid = validated_data.pop("name_uuid")
        company_check_obj = CompanyCheck.objects.get(
            name_uuid=name_uuid)

        company = Company.objects.create(
            company_check=company_check_obj, **validated_data)

        return company


class CompanyDescSerializer(serializers.ModelSerializer):

    company_check = CheckingCompanySerializer()

    class Meta:
        model = Company
        fields = "__all__"
