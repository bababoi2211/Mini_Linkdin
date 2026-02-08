

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model


class UserCreationForm(forms.ModelForm):

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput())
    password2 = forms.CharField(
        label="Password Confirmation", widget=forms.PasswordInput()
    )

    class Meta:
        model = get_user_model()
        fields = ('username', "email", "phone_number", "legal_name")

    def clean_password2(self):

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if not ((password1 and password2) and (password1 == password2)):
            raise ValidationError("Password don't match")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
            
        return user

        
    

class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField(
        help_text="you can change password using <a href =\"../password/\">this form</a> ")

    class Meta:
        model = get_user_model()
        fields = ('username', "email", 'phone_number', 'legal_name',
                  'password')



class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())