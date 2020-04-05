import os
import time

from bootstrap_modal_forms.generic import BSModalDeleteView
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import generic, View
from django.views.generic import CreateView, UpdateView

from .forms import BookForm, PhotoForm
from .models import Book, Photo


@method_decorator(login_required, name='dispatch')
class BooksListView(generic.ListView):
    model = Book
    template_name = 'books/list_of_books.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.filter(seller=self.request.user)
        return context


@method_decorator(login_required, name='dispatch')
class BookCreateView(CreateView):
    template_name = 'books/create_book.html'
    form_class = BookForm
    success_message = 'Success: Book was created.'

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

    def get_success_url(self):
        slug = self.object.slug
        return reverse_lazy('books:upload', kwargs={'slug': slug})


@method_decorator(login_required, name='dispatch')
class BookUpdateView(UpdateView):
    model = Book
    template_name = 'books/update_book.html'
    form_class = BookForm
    success_message = 'Success: Book was updated.'

    def get_success_url(self):
        slug = self.object.slug
        return reverse_lazy('books:upload', kwargs={'slug': slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = Photo.objects.filter(book=self.object)
        return context


@method_decorator(login_required, name='dispatch')
class BookDeleteView(BSModalDeleteView):
    model = Book
    template_name = 'books/delete_book.html'
    success_message = 'Success: Book was deleted.'
    success_url = reverse_lazy('books:list')


def delete_file(request, pk):
    for file in Photo.objects.filter(id=pk):
        file.delete()
    root = settings.MEDIA_ROOT + '/books_img'
    folders = list(os.walk(root))[1:]

    for folder in folders:
        if not folder[2]:
            os.rmdir(folder[0])
    return HttpResponseRedirect(request.POST.get('next'))


class ProgressBarUploadView(View):
    def get(self, request, slug):
        book = Book.objects.get(slug=slug)
        photos_list = Photo.objects.filter(book=book)
        try:
            context = {
                'book': book,
                'photos': photos_list
            }
            return render(self.request, 'books/upload.html', context)
        except ObjectDoesNotExist:
            return render(self.request, 'books/upload.html')

    def post(self, request, **kwargs):
        time.sleep(1)
        form = PhotoForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            slug = self.kwargs['slug']
            form.instance.book = Book.objects.get(slug=slug)
            photo = form.save()
            data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)
