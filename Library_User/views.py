from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import FormView, DetailView, CreateView
from .forms import RegisterForm
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from .forms import DepositForm, CommentForm
from django.views.generic import TemplateView
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from . import models  
from Library.models import BookModel, Category
from .models import BorrowedBookModel

#============================= For Email=================================#
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

def send_transaction_email(user, amount, subject, template):
    message = render_to_string(template, {
        'user' : user,
        'amount' : amount,
    })
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()

#=======================================UserRegistrationViews======================#

class UserRegistrationViews(FormView):
    template_name = 'user_registration.html'
    form_class = RegisterForm
    success_url =reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form) 
#=======================================Userloginviews===============================#
class Userloginviews(LoginView):
    template_name = 'user_login.html'
    
    def get_success_url(self):
        return reverse_lazy('home')

#=======================================Userlogoutview===============================#   
class userlogoutview(View):
    def get(self, request):
        logout(request)
        return redirect('home')
    


#=======================================Deposite Money===============================#
    
def deposit_money(request):
    user_account = request.user.account  
    
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            user_account.balance += amount
            user_account.save()
            messages.success(
            request,
            f'{"{:,.2f}".format(float(amount))}$ is deposited to your account successfully'
            )

            send_transaction_email(request.user, amount, "Deposit Message", "deposit_email.html")
            return redirect('home')  
        

    else:
        form = DepositForm()

    return render(request, 'deposit_money.html', {'form': form})

#=======================================profileview===============================#
class profileview1(TemplateView):
    template_name = 'profile.html'

def profileview(request):
    data = BorrowedBookModel.objects.filter(user=request.user)
    
    return render(request, 'profile.html', {'data':data})

def showBookview(request, category_slug = None):
    data = BookModel.objects.all()
    if category_slug is not None:
        category = Category.objects.get(slug = category_slug)
        data = BookModel.objects.filter(category = category)
        
    categories = Category.objects.all()
    return render(request, 'show_book.html', {'data':data, 'category': categories})



#=======================================BookDetailsView===============================#
class BookDetailsView(DetailView):
    model = BookModel
    # pk_url_kwarg = 'id'
    template_name = 'book_details.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        comments = book.comments.all()
        comment_form = CommentForm()
        context['comments'] = comments
        context['comment_form'] = comment_form
        context['book'] = book
        return context
    
#=======================================Borrowed_Book===============================#

def Borrowed_Book(request, id):
    book = get_object_or_404(BookModel, pk=id)

    user_balance = int(request.user.account.balance)
    borrowing_price = int(book.borrowing_price)

    if user_balance >= borrowing_price:
        BorrowedBookModel.objects.create(user=request.user, book=book)
        request.user.account.balance -= borrowing_price
        request.user.account.save()
        messages.success(
            request,
            f'{"{:,.2f}".format(float(borrowing_price))}$ is borrowed book successfully'
            )

        send_transaction_email(request.user, borrowing_price, "Borrowed Book Message", "borrowed_book_email.html")
    else:
        messages.success(
            request,
            f'{"{:,.2f}".format(float(borrowing_price))}$ Borrowing price is more than your account balance. Please deposit more'
            )

    return redirect(reverse("book_details", args=[book.id]))


 
#=======================================Return_book===============================#

def Return_book(request, id):
    record = BorrowedBookModel.objects.get(pk=id)
    print(record.book.borrowing_price)

    request.user.account.balance += int(record.book.borrowing_price)
    request.user.account.save()

    record.delete()
    messages.success(
        request,
        f' Borrowed book is returned successfully'
        )

    send_transaction_email(request.user, int(record.book.borrowing_price), "Return Book Message", "return_book_email.html")
    return redirect('profile')

#=======================================Comment_views===============================#

class Comment_views(DetailView):
    model = BookModel
    # pk_url_kwarg = 'id'
    template_name = 'comment.html'
 
    def post(self, request, *args, **kwargs):
        comment_form = CommentForm(data=self.request.POST)
        book = self.get_object()
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.book = book
            new_comment.user = request.user
          
            
            new_comment.save()
        return self.get(request, *args, **kwargs)
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object
        comments = book.comments.all()
        comment_form = CommentForm()
        context['comments'] = comments
        context['comment_form'] = comment_form
        context['book'] = book
        return context
    
    
    
