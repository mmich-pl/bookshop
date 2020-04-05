import os

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from star_ratings.models import Rating


def content_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.user.username, ext)
    return os.path.join('profile_img', filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    birthdate = models.DateField(null=True, blank=True)
    email = models.EmailField(max_length=100, null=True)
    phone = models.CharField(max_length=9, null=True)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)
    ratings = GenericRelation(Rating)

    def __str__(self):
        if self.first_name and not self.last_name:
            return self.first_name
        elif self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        else:
            return 'User' + ' ' + str(self.user)


class SocialMedia(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    facebook = models.URLField(max_length=250, blank=True, null=True)
    twiter = models.URLField(max_length=250, blank=True, null=True)
    instagram = models.URLField(max_length=250, blank=True, null=True)

    def __str__(self):
        return 'SocialMedia' + ' ' + str(self.user)

    class Meta:
        verbose_name_plural = "SocialMedia"


class ProfileImage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='photo')
    file = models.ImageField(upload_to=content_file_name)
    uploaded_at = models.DateTimeField(auto_now_add=True)
