import logging
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm

logger = logging.getLogger('auth')


def signup(request):
    """Register a new user."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(f'{str(datetime.now())}: {user.username} has successfully registered an account')
        else:
            messages.error(request, "Your form is invalid! please fill out again.")
            logger.info(f'{str(datetime.now())}: {form.username} has failed to registered an account')
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
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password'),
            )
            if user is not None:
                login(request, user)
                logger.info(f'{str(datetime.now())}: {user.username} has successfully logged in')
                messages.success(request, f"Welcome {user.username}")
                return redirect("qa_rpg:index")
        messages.error(request, "Your form is invalid! please fill out again.")
        logger.info(f'{str(datetime.now())}: {form.cleaned_data.get("username")} has failed to log in')
        return redirect('login')
    form = LoginForm()
    return render(request=request,
                  template_name='account/login.html',
                  context={'form': form})


@login_required
def custom_logout(request):
    logger.info(f'{str(datetime.now())}: {request.user} has logged out')
    logout(request)
    return redirect('login')


def policy(request):
    print(request)
    return render(request, 'account/Privacy_Notice.html')
