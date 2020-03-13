from django.urls import path
from . import views

urlpatterns = [
    path('profile/<int:pk>', views.profile, name='profile'),
    path('profile/<int:pk>/edit', views.ProfileUpdateView.as_view(), name='profile_edit'),
]

