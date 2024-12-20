from django.urls import path
from . import views

urlpatterns = [
    path('bookapi/', views.BookApiView.as_view(), name='book-api'),
    path('bookapi/<int:pk>/', views.BookDetailApiView.as_view(), name='book-detail-api'),  
    path('adminlogin/', views.AdminLoginView.as_view(), name='admin-login'),
    path('borrow/<int:pk>/',views.BorrowBookView.as_view(),name='borrow-book'),
    path('register/',views.RegisterView.as_view(),name='register'),
    path('login/',views.LoginView.as_view(),name='login'),
    path('return/<int:book_id>/',views.ReturnBookApiView.as_view(),name='return-book'),
    path('available/',views.AvailableBooksView.as_view(),name='available'),
    path('memberborrowed/',views.MemberBorrowedBooksView.as_view(),name='member-borrow')

]