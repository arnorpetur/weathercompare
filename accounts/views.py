from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import SignupForm
from .models import UserInfo
from .emailhelper import email_logged, get_location


def signup_user(request):
    """Signup user if form is validated, else render site again"""
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            query_log = UserInfo(user=user)
            query_log.search_history = []
            if email_logged(user):
                location = get_location(request)
                if location:
                    query_log.current_city = location
                else:
                    query_log.current_city = ''
            else:
                query_log.current_city = ''
            query_log.save()
            login(request, user)
            return redirect('/')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_user(request):
    """Login User"""
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if email_logged(user):
                query_log = UserInfo.objects.get(user=user)
                location = get_location(request)
                if location:
                    query_log.current_city = location
                    query_log.save()

            login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/')