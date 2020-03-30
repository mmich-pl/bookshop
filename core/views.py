from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, View
from .forms import SignUpForm, CheckoutForm, PaymentForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .models import OrderBook, Order, Address, Payment
from profiles.models import Profile
from books.models import Book, Photo
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib import messages
from .decorators import anonymous_required
from django.utils.decorators import method_decorator
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
from django.conf import settings
import json

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_account(self, form):
    user = form.save(commit=False)
    user.is_active = False
    user.save()
    current_site = get_current_site(self.request)
    email_subject = 'Activate your account.'
    message = render_to_string('core/email_templates/account_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    to_email = form.cleaned_data.get('email')
    email = EmailMessage(
        email_subject, message, to=[to_email]
    )
    email.send()
    messages.info(self.request, 'Please confirm your email address to complete the registration')
    return render(self.request, 'core/messages.html')


def validate_username_or_email(request):
    username = request.GET.get('username', None)
    email = request.GET.get('email', None)
    data = {
        'username_is_taken': User.objects.filter(username__iexact=username).exists(),
        'email_is_taken': User.objects.filter(email__iexact=email).exists()
    }
    if data['username_is_taken']:
        data['username_error_message'] = 'A user with this username already exists.'
    if data['email_is_taken']:
        data['email_error_message'] = 'A user with this email already exists.'
    return JsonResponse(data)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Your account is active!')
        return redirect('core:home')
    else:
        return HttpResponse('Activation link is invalid!')


@method_decorator(anonymous_required, name='dispatch')
class SignUpView(CreateView):
    model = User
    form_class = SignUpForm
    template_name = 'registration/signup.html'

    def form_valid(self, form, **kwargs):
        return create_account(self, form)


def home(request):
    book_list = Book.objects.all().order_by('-date')
    query = request.GET.get('q')
    if query:
        book_list = Book.objects.filter(
            Q(title__icontains=query) | Q(category__icontains=query) |
            Q(author__contains=query) | Q(publisher__contains=query)
        ).distinct()

    paginator = Paginator(book_list, 34)
    page = request.GET.get('page')

    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)

    for i in book_list:
        try:
            order = OrderBook.objects.filter(book__slug=i.slug)
            if i.amount == 0 and i.date <= (datetime.today() - timedelta(days=3)).date() and order.ordered:
                i.delete()
        except ObjectDoesNotExist:
            continue

    context = {
        'books': books,
        'categories': Book.objects.all().values('category').annotate(Count('category')).order_by('category'),
    }

    if book_list.count() > 14:
        context['most_popular'] = Book.objects.all().exclude(amount=0).order_by('-numbers_of_entries')[:7]
        context['latest'] = Book.objects.all().exclude(amount=0).order_by('-date')[:7]
        context['random'] = Book.objects.all().exclude(amount=0).order_by('?')[:7]

    return render(request, "core/home.html", context)


class BookDetailView(DetailView):
    model = Book
    template_name = "core/product.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object.numbers_of_entries = self.object.numbers_of_entries + 1
        date = self.object.date
        if datetime.today().date() <= date + timedelta(days=20):
            self.object.discount_price = self.object.price
        elif datetime.today().date() <= date + timedelta(days=40):
            self.object.discount_price = self.object.price - (self.object.price * 0.10)
        elif datetime.today().date() <= date + timedelta(days=50):
            self.object.discount_price = self.object.price - self.object.price * 0.15
        else:
            self.object.discount_price = self.object.price - self.object.price * 0.20
        self.object.save()

        more_books = Book.objects.filter(title=self.object.title, category=self.object.category,
                                         author=self.object.author, publisher=self.object.publisher).exclude(amount=0)
        context['amount'] = int(self.object.amount)
        context['amount_json'] = json.dumps(int(self.object.amount))
        context['photos'] = Photo.objects.filter(book=self.object)
        if more_books.count() > 1:
            context['more_books'] = more_books.difference(Book.objects.filter(pk=self.object.pk))
        else:
            context['more_books'] = None

        return context


@login_required
def add_to_cart(request, slug):
    book = get_object_or_404(Book, slug=slug)
    order_book, created = OrderBook.objects.get_or_create(book=book, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.books.filter(book__slug=book.slug).exists():
            book.amount -= 1
            book.save()
            order_book.quantity += 1
            order_book.save()
            messages.info(request, "This book quantity was updated.")
            return redirect("core:order_summary")
        else:
            book.amount -= 1
            book.save()
            order.books.add(order_book)
            messages.info(request, "This book was added to your cart.")
            return redirect("core:product", slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        book.amount -= 1
        book.save()
        order.books.add(order_book)
        messages.info(request, "This book was added to your cart.")
        return redirect("core:product", slug=slug)


@login_required
def remove_from_cart(request, slug):
    book = get_object_or_404(Book, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.books.filter(book__slug=book.slug).exists():
            order_book = OrderBook.objects.filter(book=book, user=request.user, ordered=False)[0]
            if order_book.quantity >= 1:
                book.amount += order_book.quantity
            else:
                book.amount += 1
            book.save()
            order_book.quantity = 0
            order.books.remove(order_book)
            order_book.delete()
            messages.info(request, "This book was removed from your cart.")
            return redirect("core:order_summary")
        else:
            messages.info(request, "This book was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_book_from_cart(request, slug):
    book = get_object_or_404(Book, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.books.filter(book__slug=book.slug).exists():
            order_book = OrderBook.objects.filter(book=book, user=request.user, ordered=False)[0]
            if order_book.quantity > 1:
                order_book.quantity -= 1
                order_book.save()
                book.amount += 1
                book.save()
            else:
                remove_from_cart(request, slug)
            messages.info(request, "This book quantity was updated.")
            return redirect("core:order_summary")
        else:
            messages.info(request, "This book was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


@method_decorator(login_required, name='dispatch')
class OrderSummaryView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
            }
            return render(self.request, 'core/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active orders!")
            return redirect("core:home")


@method_decorator(login_required, name='dispatch')
class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'form': form,
            'order': order
        }

        address_qs = Address.objects.filter(user=self.request.user, default=True)
        if address_qs.exists():
            context.update({'default_address': address_qs[0]})

        return render(self.request, "core/checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                use_default = form.cleaned_data.get('use_default')
                if use_default:
                    print("Using the default shipping address")
                    address_qs = Address.objects.filter(user=self.request.user, default=True)
                    if address_qs.exists():
                        address = address_qs[0]
                        order.address = address
                        order.save()
                    else:
                        messages.warning(self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new address")
                    address_form_form = form.cleaned_data.get('street_address')
                    apartment_address = form.cleaned_data.get('apartment_address')
                    country = form.cleaned_data.get('country')
                    city = form.cleaned_data.get('city')
                    zip = form.cleaned_data.get('zip')

                    if is_valid_form([address_form_form, apartment_address, country, city, zip]):
                        address = Address(user=self.request.user, street_address=address_form_form,
                                          apartment_address=apartment_address, country=country, city=city,
                                          zip=zip)
                        address.save()
                        order.address = address
                        order.save()
                        set_default = form.cleaned_data.get('set_default')
                        if set_default:
                            address_qs = Address.objects.filter(user=self.request.user, default=True)
                            if address_qs.count() > 0:
                                for i in address_qs:
                                    i.delete()
                            address.default = True
                            address.save()
                    else:
                        messages.warning(self.request, "Please fill in the required shipping address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                else:
                    messages.warning(self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order- summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order
        }
        user_profile = Profile.objects.get(user=self.request.user)
        if user_profile.one_click_purchasing:
            cards = stripe.Customer.list_sources(
                user_profile.stripe_customer_id,
                limit=3,
                object='card'
            )
            card_list = cards['data']
            if len(card_list) > 0:
                context.update({
                    'card': card_list[0]
                })

        return render(self.request, "core/payment.html", context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        user_profile = Profile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            print(token)
            print(save)
            print(use_default)

            if save:
                if user_profile.stripe_customer_id != '' and user_profile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(user_profile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(email=self.request.user.email,)
                    customer.sources.create(source=token)
                    user_profile.stripe_customer_id = customer['id']
                    user_profile.one_click_purchasing = True
                    user_profile.save()

            amount = int(order.get_total() * 100)
            try:
                print("sanity")
                if use_default or save:
                    charge = stripe.Charge.create(amount=amount, currency="pln",
                                                  customer=user_profile.stripe_customer_id)
                else:
                    charge = stripe.Charge.create(amount=amount, currency="pln", source=token)

                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                order_books = order.books.all()
                order_books.update(ordered=True)
                for book in order_books:
                    book.save()

                order.ordered = True
                order.payment = payment
                order.save()
                messages.success(self.request, "Your order was successful!")
                return redirect("core:home")

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("core:home")

            except stripe.error.RateLimitError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                messages.warning(self.request, "Rate limit error")
                return redirect("core:home")

            except stripe.error.InvalidRequestError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                messages.warning(self.request, "Invalid parameters")
                return redirect("core:home")

            except stripe.error.AuthenticationError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                messages.warning(self.request, "Not authenticated")
                return redirect("core:home")

            except stripe.error.APIConnectionError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                messages.warning(self.request, "Network error")
                return redirect("core:home")

            except stripe.error.StripeError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                messages.warning(self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("core:home")

            except Exception as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                messages.warning(self.request, "A serious error occurred. We have been notifed.")
                return redirect("core:home")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")
