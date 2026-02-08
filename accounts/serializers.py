

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
import uuid
import re
import pytz
from typing_extensions import Callable
from .models import WorkProfile
import datetime
from copy import copy

def limited_char(value):
    if len(value) != 11:
        raise ValidationError("The lenght is incorrect")


class UserSerializers(serializers.Serializer):

    username = serializers.CharField()
    email = serializers.EmailField()
    legal_name = serializers.CharField(max_length=20)
    phone_number = serializers.CharField(validators=[limited_char,])

    def validate_username(self, value):
        if re.search(r'[_@#$%^&*()+=|<>?{}\[\]]', value):
            raise serializers.ValidationError("Invalid symbol in username")

        elif re.match("[_]", value):
            raise serializers.ValidationError(
                "Invalid symbol in username in start ")

        return value

    def validate_uuid(self, value):
        try:
            u = uuid.UUID(value)

        except ValueError:
            raise serializers.ValidationError('Error The UUid Isnt correct!')
        return u


class UserRegisterySerializer(serializers.ModelSerializer):
    password2 = serializers.CharField()

    class Meta:
        model = get_user_model()
        fields = ('username', 'phone_number', 'email',
                  'legal_name', 'password', 'password2')

        extra_kwargs = {

            'username': {'write_only': True},
            'phone_number': {"validators": [limited_char,]},
            'password': {"write_only": True}

        }

    def validate(self, attrs):

        password1 = attrs['password']
        password2 = attrs['password2']

        if (password1 and password2) and password1 != password2:

            raise serializers.ValidationError("Passwords Doesnt match")
        return attrs

    def validate_uuid(self, value):
        try:
            u = uuid.UUID(value)
        except ValueError:
            raise serializers.ValidationError('Error The UUid Isnt correct!')
        return u

    def create(self, validated_data) -> Callable:
        validated_data.pop('password2')
        user = get_user_model().objects.create_user(
            validated_data['username'], validated_data['phone_number'], validated_data['email'], validated_data['legal_name'], validated_data['password'])

        user.save()

        return user

    def delete(self, username):
        get_user_model().objects.get(username=username).delete()
        return True


class UserLoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):

        username = data.get('username')
        password = data.get('password')

        if not username and not password:
            raise serializers.ValidationError(
                'Both username and password is required')

        return data


class CustomeObtainPairSerializer(TokenObtainPairSerializer):

    # Build the payload in here
    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)

        # custome fields

        token['username'] = user.username
        token['phone_number'] = user.phone_number

        return token

    def validate(self, attrs):
        User = get_user_model()
        username = attrs.get('username')
        password = attrs.get('password')
        # phone_number = self.context['request'].data.get(
        #     "phone_number")  # from requested data

        if not username or not password:
            raise serializers.ValidationError(
                "Username and password are required.")

        try:
            user = User.objects.get(
                username=username,)

            if not user.phone_number:
                raise serializers.ValidationError("Phone Number is required")

        except User.DoesNotExist as err:
            raise serializers.ValidationError("Invalid credentials")

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        refresh = RefreshToken.for_user(user)
        # Add to the payload token
        refresh['username'] = user.username
        refresh['phone_number'] = user.phone_number

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
