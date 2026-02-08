
from rest_framework import serializers

from accounts.models import WorkProfile
import datetime
import pytz
import copy

from rest_framework import status


class WorkProfileSerializers(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = WorkProfile
        fields = "__all__"

        extra_kwargs = {
            'user': {"read_only": True}
        }

    def validate(self, attrs):
        try:

            date_from = attrs['work_span_from']
            date_till = attrs["work_span_till"]
        except KeyError:
            raise serializers.ValidationError(
                {"detail": "Didnt Provide the date."})

        correct_date = datetime.datetime.now(pytz.timezone(
            "Asia/Tehran")) - datetime.timedelta(days=1)
        if date_from > correct_date:

            raise serializers.ValidationError(
                'Work start date must be before today.')

        if date_from > date_till:
            raise serializers.ValidationError("The working time is incorrect")

        return attrs

    def validate_job_title(self, value):

        if not value:
            raise serializers.ValidationError("Please Specify your job")

        return value.replace(" ", "-")

    def create(self, validated_data):

        validated_datas = copy(validated_data)
        user = validated_datas.pop('user')

        work_profile = WorkProfile.objects.create(user=user, **validated_datas)
        return work_profile

    def update(self, instance, validated_data):
        if validated_data.get("user"):

            raise serializers.ValidationError(
                {"detail": "Cant Edit user"}, code=status.HTTP_401_UNAUTHORIZED)

        return super().update(instance, validated_data)
