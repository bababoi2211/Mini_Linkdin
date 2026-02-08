
from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .forms import UserChangeForm, UserCreationForm
from . import models
import hashlib


class ProfileInline(admin.StackedInline):
    model = models.WorkProfile
    extra = 0
    fieldsets = (
        ('Work Role', {"fields": ('company',
         'job_title', 'rank', "avg_hourly_incomes",'job_category')}),
        ('To Add', {"fields": ('description',)}),
        ('Exprience', {"fields": ('work_span_from',
         'work_span_till', 'total_experience_months'), "description": 'total_experience_months Will be automatically counted (Need To be Saved) '})
    )

    readonly_fields = ('total_experience_months',)
    can_delete = True

    

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    inlines = [ProfileInline,]
    list_display = ('phone_number',
                    'email', 'is_admin')
    list_filter = ('is_admin',)

    fieldsets = (
        ('Info User', {
         'fields': ('username', 'phone_number', 'email', 'legal_name', 'password')}),
        ('UUID', {'fields': ('id',)}),
        ('Permissions', {'fields': ('is_active', 'is_admin',
         'last_login', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {'fields': ('username', 'phone_number', 'email',
                           'legal_name', 'password1', 'password2')}),
        ("permission", {"fields": ('is_active', "is_admin", "is_superuser")})
    )

    search_fields = ('email', 'legal_name')

    ordering = ('phone_number',)
    filter_horizontal = ('groups', 'user_permissions')
    readonly_fields = ("last_login", 'id')

    def get_form(self, request, obj=..., change=..., **kwargs):

        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser

        if not is_superuser:
            for item in ['is_superuser', 'is_admin',
                         'is_active', 'username']:
                form.base_fields[item].disabled = True

        # if obj and request.user.phone_number != obj.phone_number:
        #     form.base_fields['username', 'phone_number'].disabled = True

        return form


admin.site.register(get_user_model(), UserAdmin)
