from django.urls import reverse_lazy
from django.views import generic
from .forms import BookForm
from .models import Book
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, \
                                          BSModalReadView, BSModalDeleteView


class BooksListView(generic.ListView):
    model = Book
    context_object_name = 'books'
    template_name = 'books/list_of_books.html'


class BookCreateView(BSModalCreateView):
    template_name = 'books/create_book.html'
    form_class = BookForm
    success_message = 'Success: Book was created.'
    success_url = reverse_lazy('list')

    def form_valid(self, form, **kwargs):
        form.instance.seller = self.request.user
        form.instance.discount_price = float(form.cleaned_data['price'])
        title = form.cleaned_data['title'].strip()
        form.instance.slug = title.replace(" ", "-")
        return super().form_valid(form)


class BookUpdateView(BSModalUpdateView):
    model = Book
    template_name = 'books/update_book.html'
    form_class = BookForm
    success_message = 'Success: Book was updated.'
    success_url = reverse_lazy('list')


class BookDeleteView(BSModalDeleteView):
    model = Book
    template_name = 'books/delete_book.html'
    success_message = 'Success: Book was deleted.'
    success_url = reverse_lazy('list')