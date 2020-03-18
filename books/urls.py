from django.urls import path
from books import views

urlpatterns = [
    path('book/list', views.BooksListView.as_view(), name='list'),
    path('book/create/', views.BookCreateView.as_view(), name='create_book'),
    path('book/update/<int:pk>', views.BookUpdateView.as_view(), name='update_book'),
    path('book/delete/<int:pk>', views.BookDeleteView.as_view(), name='delete_book')
]