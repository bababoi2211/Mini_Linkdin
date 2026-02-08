
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import JsonResponse


from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import SAFE_METHODS, IsAdminUser, IsAuthenticated, AllowAny
from rest_framework import status


from . import permissions, serializers
from accounts.models import WorkProfile as ProfileObj


class WorkProfileView(viewsets.ViewSet):

    renderer_classes = [JSONRenderer,]

    def setup(self, request, *args, **kwargs):
        self.User = get_user_model()

        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):

        pk = kwargs.get("pk")
        if pk:

            user = get_object_or_404(get_user_model(), pk=pk)

            self.target_user = user

            # if not request.method in SAFE_METHODS:
            # if request.user != user and not request.user.is_staff:

            # return JsonResponse({"detail": "NOt the same user"}, status=status.HTTP_403_FORBIDDEN)

        self.company_name_query = request.GET.get("company_name")

        return super().dispatch(request, *args, **kwargs)

    def get_permissions(self):

        if self.action == 'create':
            permission_classes = [permissions.IsOwnerOrReadOnly]

        elif self.action == "list":
            permission_classes = [IsAdminUser]

        elif self.action == "create":
            # permission_classes = [IsAuthenticated]
            permission_classes = [AllowAny]

        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated]

        elif self.action == 'partial_update':
            permission_classes = [permissions.IsOwnerOrReadOnly]

        else:
            permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]

    def retrieve(self, requets, pk=None):
        # user = get_object_or_404(self.__User(), pk=pk)

        work_profile = ProfileObj.objects.filter(user=self.target_user)

        if self.company_name_query:
            work_profile = ProfileObj.objects.filter(
                user=self.target_user, company=self.company_name_query)

        total_companies = work_profile.values('company').distinct().count()

        ser_data = serializers.WorkProfileSerializers(
            instance=work_profile, many=True)

        data = {
            'profiles': ser_data.data,
            'total_companies': total_companies
        }
        return Response(data=data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """This Function Will delete all of the work profile """
        # user = get_object_or_404(self.__User(), pk=pk)
        user = self.target_user
        user.profile.all().delete()
        return Response({"message": "Deleted All Work Profile"}, status=status.HTTP_202_ACCEPTED)

    def partial_update(self, request, *args, **kwargs):

        pk = kwargs.get("pk")
        company_name = request.GET.get("company_name")

        if not (pk and company_name):
            return Response({"detail": "No user uuid and no company name"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(get_user_model(), pk=pk)

        try:

            work_profile_instance = ProfileObj.objects.get(
                user=user, company=company_name)

            ser_data = serializers.WorkProfileSerializers(
                instance=work_profile_instance, data=request.data, partial=True)

            ser_data.is_valid(raise_exception=True)

            ser_data.save()

            return Response({"detail": "Work profile updated"}, status=status.HTTP_204_NO_CONTENT)

        except ProfileObj.DoesNotExist:
            return Response({"detail": "No Such profile exists"}, status=status.HTTP_400_BAD_REQUEST)


class DeleteWorkProfileView(APIView):
    """Delete specified work profile    """
    permission_classes = [permissions.IsOwnerOrReadOnly,]

    def delete(self, request, *args, **kwargs):

        user = request.user
        if not user.id == kwargs['user_uuid']:
            return Response({"detail": "User doesnt have access"},
                            status=status.HTTP_401_UNAUTHORIZED)

        workprofile = get_object_or_404(
            ProfileObj, company=kwargs["company_name"], user=user)

        self.check_object_permissions(request, workprofile)

        workprofile.delete()

        return Response({"detail": "work profile Deleted"}, status=status.HTTP_200_OK)


class CreateWorkProfile(APIView):

    """
    data sent:

    {"user":1,
     "info":
         {"company":"","job_title":"","rank":"","avg_hourly_incomes":"","description":"","work_span_from":"","work_span_till":"","total_experience_months":""}}

         OR

     "info":
         {"company":"","job_title":"","rank":"","avg_hourly_incomes":"","description":"","work_span_from":"","work_span_till":"","total_experience_months":""},
         {"company":"","job_title":"","rank":"","avg_hourly_incomes":"","description":"","work_span_from":"","work_span_till":"","total_experience_months":""}
         }
    """

    permission_classes = [IsAuthenticated,]

    def post(self, request, *args, **kwargs):

        user = request.user

        if not user.id == kwargs["user_uuid"]:
            return Response({"detail": "User doesnt have access"},
                            status=status.HTTP_401_UNAUTHORIZED)
        try:

            ser_data = serializers.WorkProfileSerializers(data=request.data)
            ser_data.is_valid(raise_exception=True)
            print(ser_data.validated_data)

            work_profile = ser_data.save(user=user)

        except Exception as err:
            return Response({"detail": f"Un expected Error {err}"})

        return Response(serializers.WorkProfileSerializers(work_profile).data, status=status.HTTP_200_OK)
