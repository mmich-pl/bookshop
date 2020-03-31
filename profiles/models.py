from django.contrib.auth.models import User
from django.db import models
from PIL import Image
from star_ratings.models import Rating
from django.contrib.contenttypes.fields import GenericRelation


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    birthdate = models.DateField(null=True, blank=True)
    picture = models.ImageField(default='default.jpg', upload_to='profile_pics')
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

    def save(self, **kwargs):
        super().save()

        img = Image.open(self.picture.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.picture.path)


class SocialMedia(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    facebook = models.URLField(max_length=250, blank=True, null=True)
    twiter = models.URLField(max_length=250, blank=True, null=True)
    instagram = models.URLField(max_length=250, blank=True, null=True)

    def __str__(self):
        return 'SocialMedia' + ' ' + str(self.user)

    class Meta:
        verbose_name_plural = "SocialMedia"
