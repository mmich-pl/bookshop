from .models import Book
from bootstrap_modal_forms.forms import BSModalForm


class BookForm(BSModalForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'publisher', 'category', 'condition', 'price', 'description', 'image']
