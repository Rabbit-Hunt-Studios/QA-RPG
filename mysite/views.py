from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm


def signup(request):
    """Register a new user."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
        else:
            messages.error(request, "Your form is invalid! please fill out again.")
            return redirect('signup')
        return redirect('login')
    else:
        form = RegisterForm()
    return render(request=request,
                  template_name='account/signup.html',
                  context={'form': form})

def custom_login(request):
    """Log in."""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data.get('username'),
                raw_passwd=form.cleaned_data.get('password'),
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome {user.username}")
        else:
            messages.error(request, "Your form is invalid! please fill out again.")
            return redirect('login')
    form = LoginForm()
    return render(request=request,
                  template_name='account/login.html',
                  context={'form': form})

@login_required
def custom_logout(request):
    logout(request)
    return redirect('login')

def policy(request):
    print(request)
    return render(request, 'account/Privacy_Notice.html')
