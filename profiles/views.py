from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from books.models import Book
from core.models import Payment, Order, Address
from .forms import ProfileForm, SocialMediaForm, AddressForm, ProfileImageForm
from .models import Profile, SocialMedia, ProfileImage


@method_decorator(login_required, name='dispatch')
class ProfileView(View):

    def get(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=kwargs['pk'])
            try:
                socialMedia = SocialMedia.objects.get(user=kwargs['pk'])
                address = Address.objects.get(user=request.user, default=True)
                picture = ProfileImage.objects.get(user=profile.user)

            except ObjectDoesNotExist:
                socialMedia = ''
                address = ''
                picture = ''

            user = Profile.objects.get(user=request.user)
            form = AddressForm()
            payments = Payment.objects.filter(user=request.user)
            orders = Order.objects.filter(user=request.user)
            books = Book.objects.filter(seller=profile.user)
            form_profile_image = ProfileImageForm()
            context = {
                'socialMedia': socialMedia,
                'profile': profile,
                'user': user,
                'form': form,
                'form_profile_image': form_profile_image,
                'payments': payments,
                'orders': orders,
                'address': address,
                'books': books,
                'picture': picture,
            }
            return render(self.request, 'profiles/profile.html', context)
        except AttributeError:
            messages.warning(self.request, "Something went wrong, try again later")
            return redirect('core:home')

    def post(self, request, *args, **kwargs):
        if not request.user.id == self.kwargs.get('pk'):
            raise Http404

        if 'profile_edit' in request.POST and request.method == 'POST':
            instance = get_object_or_404(Profile, user=request.user)
            form = ProfileForm(self.request.POST or None, instance=instance)
            if form.is_valid():
                print("sanity check")
                form.save(commit=False)
                form.email = request.user.email
                form.save()

        elif 'address_edit' in request.POST and request.method == 'POST':

            form = AddressForm(self.request.POST or None)
            if form.is_valid():
                address_form_form = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                city = form.cleaned_data.get('city')
                zip = form.cleaned_data.get('zip')
                try:
                    address = Address.objects.get(user=request.user, default=True)
                    address.user = self.request.user
                    address.street_address = address_form_form
                    address.apartment_address = apartment_address
                    address.country = country
                    address.city = city
                    address.zip = zip
                    address.save()

                except ObjectDoesNotExist:
                    address = Address(user=self.request.user, street_address=address_form_form,
                                      apartment_address=apartment_address, country=country, city=city,
                                      zip=zip, default=True)
                    address.save()
            else:
                messages.warning(self.request, "Please fill in the required fields")

        elif 'socialMedia_edit' in request.POST and request.method == 'POST':
            instance, created = SocialMedia.objects.get_or_create(user=request.user)
            if created:
                form = SocialMediaForm(self.request.POST, instance=created)
                if form.is_valid():
                    form.save()
            else:
                form = SocialMediaForm(self.request.POST, instance=instance)
                if form.is_valid():
                    form.save()
        else:
            form = ProfileImageForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    picture = ProfileImage.objects.get(user=request.user)
                    picture.file.delete()
                    picture.delete()
                    form.instance.user = request.user
                    form.save()
                    messages.info(request, "If photo doesnt change, please reload the page")
                except ObjectDoesNotExist:
                    form.instance.user = request.user
                    form.save()
                    messages.info(request, "If photo doesnt change, please reload the page")
        return redirect('profile', kwargs['pk'])
