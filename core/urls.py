from django.urls import path, include
from . import views
from django.conf.urls import url

# TODO: add other urls to navbar
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('checkout/', views.checkout, name='checkout'),
    path('product/<slug>', views.BookDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', views.remove_from_cart, name='remove-from-cart'),
    url(r'^signup/$', views.SignUpView.as_view(), name='signup'),
    url(r'^ajax/validate_username/$', views.validate_username_or_email, name='validate_username_or_email'),
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate')
]
