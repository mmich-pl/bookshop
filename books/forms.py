from django import forms
from .models import Book
from .models import Photo


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ('file', )


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'publisher', 'category', 'condition', 'amount', 'price', 'description']
