from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.generic import CreateView, DetailView
from .forms import SignUpForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .models import Book, OrderBook, Order
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


@method_decorator(anonymous_required, name='dispatch')
class SignUpView(CreateView):
    model = User
    form_class = SignUpForm
    template_name = 'registration/signup.html'

    def form_valid(self, form, **kwargs):
        return create_account(self, form)


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
        self.object.save()
        return context


def checkout(request):
    return render(request, "core/checkout.html")


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
            return redirect("core:product", slug=slug)
        else:
            order.books.add(order_book)
            messages.success(request, "This book was added to your cart.")
            return redirect("core:product", slug=slug)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.books.add(order_book)
        messages.success(request, "This book was added to your cart.")
        return redirect("core:product", slug=slug)


def remove_from_cart(request, slug):
    book = get_object_or_404(Book, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.books.filter(book__slug=book.slug).exists():
            order_book = OrderBook.objects.filter(
                book=book,
                user=request.user,
                ordered=False
            )[0]
            order.books.remove(order_book)
            messages.warning(request, "This book was removed from your cart.")
            return redirect("core:product", slug=slug)
        else:
            messages.error(request, "This book was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.error(request, "You do not have an active order")
        return redirect("core:product", slug=slug)