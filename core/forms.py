from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)


class SignUpForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CheckoutForm(forms.Form):
    # TODO: add city field
    street_address = forms.CharField(widget=forms.TextInput(
        attrs={'id': 'address'}))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'id': 'address-2'}))
    country = CountryField(blank_label='(select country)').formfield(
        widget=CountrySelectWidget(attrs={'class': 'custom-select d-block w-100',}))
    zip = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'zip'}))
    same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)