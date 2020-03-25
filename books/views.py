from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic
from .forms import BookForm
from .models import Book
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, \
                                          BSModalDeleteView


@method_decorator(login_required, name='dispatch')
class BooksListView(generic.ListView):
    model = Book
    template_name = 'books/list_of_books.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.filter(seller=self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
class BookCreateView(BSModalCreateView):
    template_name = 'books/create_book.html'
    form_class = BookForm
    success_message = 'Success: Book was created.'
    success_url = reverse_lazy('list')

    def form_valid(self, form, **kwargs):
        form.instance.seller = self.request.user
        form.instance.discount_price = float(form.cleaned_data['price'])
        title = form.cleaned_data['title'].strip()
        other = Book.objects.filter(title=form.instance.title).count()
        if other < 1:
            form.instance.slug = title.replace(" ", "-")
        else:
            form.instance.slug = str(other) + "-" + title.replace(" ", "-")
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class BookUpdateView(BSModalUpdateView):
    model = Book
    template_name = 'books/update_book.html'
    form_class = BookForm
    success_message = 'Success: Book was updated.'
    success_url = reverse_lazy('list')


@method_decorator(login_required, name='dispatch')
class BookDeleteView(BSModalDeleteView):
    model = Book
    template_name = 'books/delete_book.html'
    success_message = 'Success: Book was deleted.'
    success_url = reverse_lazy('list')
