from django import forms
from .models import Profile, SocialMedia
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'birthdate', 'phone')


class SocialMediaForm(forms.ModelForm):
    class Meta:
        model = SocialMedia
        exclude = ['user']


class AddressForm(forms.Form):
    street_address = forms.CharField()
    apartment_address = forms.CharField()
    country = CountryField(blank_label='(select country)').formfield(
        widget=CountrySelectWidget(attrs={'class': 'custom-select d-block w-100',}))
    city = forms.CharField()
    zip = forms.CharField()