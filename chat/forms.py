

from django import forms
from django.contrib.auth import get_user_model

# admins = {f"{admin.username}-{admin.legal_name}": admin.username for admin in sync_to_async(list)(get_user_model().objects.filter(is_admin=True))}


class OptionAdminForm(forms.Form):

    admin = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        
        admins = get_user_model().objects.filter(is_admin=True)
    
        self.fields["admin"].choices = [

            (admin.username, f"{admin.username}-{admin.legal_name}") for admin in admins

        ]
