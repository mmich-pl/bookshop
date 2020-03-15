from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.home, name='home'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('product/<slug>', views.BookDetailView.as_view(), name='product'),
    path('add_to_cart/<slug>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<slug>/', views.remove_from_cart, name='remove_from_cart'),
    path('remove_book_from_cart/<slug>/', views.remove_single_book_from_cart,
         name='remove_single_book_from_cart'),
    path('order_summary/', views.OrderSummaryView.as_view(), name='order_summary'),
    path('payment/<payment_option>/', views.PaymentView.as_view(), name='payment'),
    url(r'^signup/$', views.SignUpView.as_view(), name='signup'),
    url(r'^ajax/validate_username/$', views.validate_username_or_email, name='validate_username_or_email'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate')
]
