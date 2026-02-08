from rest_framework.permissions import BasePermission,SAFE_METHODS
from rest_framework.metadata import BaseMetadata




class CustomeMeta(BaseMetadata):
    def determine_metadata(self, request, view):

        return {
            "name": view.get_view_name(),
            'renderers': [renderer.media_type for renderer in view.renderer_classes],
            'type_method': request.method
        }




class AuthInCookie(BasePermission):

    def has_permission(self, request, view):
        token = request.COOKIES.get("access_token")

        if not token:
            raise PermissionError(
                "Permission Denied \n user Doesnt have auth in request")

        return True


class IsOwnerOrReadOnly(BasePermission):

    message = "Permission Denied You are not the Author"

    def has_permission(self, request, view):

        return (request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):

        if request.method in SAFE_METHODS:
            return True

        return obj.user == request.user
