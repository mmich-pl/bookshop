from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, View
from .forms import SignUpForm, CheckoutForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .models import Book, OrderBook, Order, BillingAddress, Payment
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib import messages
from .decorators import anonymous_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
from django.conf import settings

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_account(self, form):
    user = form.save(commit=False)
    user.is_active = False
    user.save()
    current_site = get_current_site(self.request)
    mail_subject = 'Activate your account.'
    message = render_to_string('core/acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
    })
    to_email = form.cleaned_data.get('email')
    email = EmailMessage(
        mail_subject, message, to=[to_email]
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

    paginator = Paginator(book_list, 12)
    page = request.GET.get('page')

    try:
        books = paginator.page(page)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)

    context = {
        'books': books,
        'latest': Book.objects.order_by('-date_posted')[:4],
    }
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
        return context


@method_decorator(login_required, name='dispatch')
class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'form': form,
            'order': order
        }
        return render(self.request, "core/checkout.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # TODO: add functionality for these fields
                # same_shipping_address = form.cleaned_data.get(
                #     'same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user, street_address=street_address, apartment_address=apartment_address,
                    country=country, zip=zip
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("core:order_summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order
        }
        return render(self.request, "core/payment.html", context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)

        try:
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="pln",
                source=token
            )

            order_books = order.books.all()
            order_books.update(ordered=True)
            for book in order_books:
                book.save()

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order.ordered = True
            order.payment = payment
            order.save()
            messages.success(self.request, "Your order was successful!")
            return redirect("core:home")

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("core:home")

        except stripe.error.RateLimitError as e:
            messages.error(self.request, "Rate limit error")
            return redirect("core:home")

        except stripe.error.InvalidRequestError as e:
            messages.error(self.request, "Invalid parameters")
            return redirect("core:home")

        except stripe.error.AuthenticationError as e:
            messages.error(self.request, "Not authenticated")
            return redirect("core:home")

        except stripe.error.APIConnectionError as e:
            messages.error(self.request, "Network error")
            return redirect("core:home")

        except stripe.error.StripeError as e:
            messages.error(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("core:home")

        except Exception as e:
            messages.error(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("core:home")

@login_required
def add_to_cart(request, slug):
    book = get_object_or_404(Book, slug=slug)
    order_book, created = OrderBook.objects.get_or_create(book=book, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.books.filter(book__slug=book.slug).exists():
            order_book.quantity += 1
            order_book.save()
            messages.info(request, "This book quantity was updated.")
            return redirect("core:order_summary")
        else:
            order.books.add(order_book)
            messages.info(request, "This book was added to your cart.")
            return redirect("core:product", slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
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
            else:
                order.books.remove(order_book)
            messages.info(request, "This book quantity was updated.")
            return redirect("core:order_summary")
        else:
            messages.info(request, "This book was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


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
