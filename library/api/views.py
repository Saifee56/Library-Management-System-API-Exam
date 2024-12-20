from django.shortcuts import render
from . models import BookModel
from . serializers import BookSerializer,AdminLoginSerializer,UserRegisterSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import now

# Crud operations for Admin
class BookApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes=[IsAuthenticated]

    def get(self,request):
        obj=BookModel.objects.all()
        serializer=BookSerializer(obj,many=True)
        return Response(serializer.data)
    
    def post(self,request):
        if not request.user.is_staff:
            return Response({"message":"Permission Denied"})
        
        data=request.data
        serializer=BookSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
class BookDetailApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_book(self, book_id):
        return BookModel.objects.filter(id=book_id).first()

    def patch(self, request, pk):
        if not request.user.is_staff:
            return Response({"message": "Permission Denied"})

        book = self.get_book(pk)
        if not book:
            return Response({"message": "Book not found"})

        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        if not request.user.is_staff:
            return Response({"message": "Permission Denied"})

        book = self.get_book(pk)
        if not book:
            return Response({"message": "Book not found"} )

        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({"message": "Permission Denied"})

        book = self.get_book(pk)
        if not book:
            return Response({"message": "Book not found"})

        book.delete()
        return Response({"message": "Book deleted successfully"})
        

# Admin-->Login and JWT authentication
class AdminLoginView(APIView):
    def post(self, request):
        data=request.data
        serializer=AdminLoginSerializer(data=data)

        if serializer.is_valid():
            username=serializer.validated_data.get('username')
            password=serializer.validated_data.get('password')

            user=authenticate(username=username,password=password)

            if user and user.is_staff:
                refresh=RefreshToken.for_user(user)

                return Response({
                    "message":"Admin Logged in successfully",
                    "access":str(refresh.access_token),
                    "refresh":str(refresh)
                })
            return Response({"message":"Invalid Credentials"})
        return Response(serializer.errors)

# User Registration View
class RegisterView(APIView):
    def post(self,request):
        data=request.data
        serializer=UserRegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"User Registered successfully"})
        return Response(serializer.errors)

# User Login View(JWT)
class LoginView(APIView):
    def post(self,request):
        username=request.data.get('username')
        password=request.data.get('password')

        user=authenticate(username=username,password=password)

        if user:
            refresh=RefreshToken.for_user(user)
            return Response({
                "message":"Login Successful",
                "access":str(refresh.access_token),
                "refresh":str(refresh)
            })
        return Response({"message":"Invalid credentials"})

# Book Borrow by User
class BorrowBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        borrowed_count = BookModel.objects.filter(
            borrowed_by=request.user,
            is_borrowed=True
        ).count()

        if borrowed_count >= 5:
            return Response(
                {"message": "You cannot borrow more than 5 books at a time"},
                status=400
            )

        # Try to borrow the book
        updated = BookModel.objects.filter(
            id=pk,
            is_borrowed=False,
            availability_status=True
        ).update(
            is_borrowed=True,
            borrowed_by=request.user,
            borrowed_at=now(),
            return_deadline=now() + timedelta(days=14),
            availability_status=False
        )

        if updated == 0:
            return Response(
                {"message": "Book is not available or already borrowed"},
                status=400
            )

        return Response({"message": "Book borrowed successfully"})
# Return Book by user

class ReturnBookApiView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request,book_id):
        try:
            book=BookModel.objects.get(id=book_id)

            if book.is_borrowed and book.borrowed_by==request.user:
                now = timezone.now()  


                if now > book.return_deadline:
                    overdue_days = (now - book.return_deadline).days
                    fine = max(0, overdue_days * 5) 
                else:
                    fine = 0
                book.is_borrowed=False  
                book.borrowed_by=None
                book.availability_status=True
                book.borrowed_at=None
                book.return_deadline=None
                book.save()
                return Response({"message":"Book Returned Successfully",
                                "fine":f"{fine} BDT" if fine>0 else "No fine"})
            else:
                return Response({"message":"You have not borrowed this book"})
        except BookModel.DoesNotExist:
            return Response({"message":"Book not found"})
        
# Available Books
class AvailableBooksView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        available_books=BookModel.objects.filter(is_borrowed=False,availability_status=True)
        serializer=BookSerializer(available_books,many=True)
        return Response(serializer.data)

# Details of borrowed books for each member
class MemberBorrowedBooksView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request):
        borrowed_books=BookModel.objects.filter(borrowed_by=request.user)
        serializer=BookSerializer(borrowed_books,many=True)
        return Response(serializer.data)

