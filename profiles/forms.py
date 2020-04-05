from PIL import Image
from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from .models import Profile, SocialMedia, ProfileImage


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
        widget=CountrySelectWidget(attrs={'class': 'custom-select d-block w-100', }))
    city = forms.CharField()
    zip = forms.CharField()


class ProfileImageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileImageForm, self).__init__(*args, **kwargs)
        self.fields['file'].label = "Change photo"
        self.label_suffix = ""

    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = ProfileImage
        fields = ('file', 'x', 'y', 'width', 'height',)

    def save(self):
        photo = super(ProfileImageForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')

        image = Image.open(photo.file)
        cropped_image = image.crop((x, y, w + x, h + y))
        resized_image = cropped_image.resize((500, 500), Image.ANTIALIAS)
        resized_image.save(photo.file.path)

        return photo
