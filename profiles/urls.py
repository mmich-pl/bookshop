from django.urls import path

from . import views

urlpatterns = [
    path('profile/<int:pk>', views.ProfileView.as_view(), name='profile'),
]
