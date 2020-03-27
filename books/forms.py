from django import forms
from .models import Book
from bootstrap_modal_forms.forms import BSModalForm
from .models import Photo


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ('file', )


class BookForm(BSModalForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'publisher', 'category', 'condition', 'amount', 'price', 'description']
