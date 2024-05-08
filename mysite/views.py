from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import RegisterForm


def signup(request):
    """Register a new user."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_passwd = form.cleaned_data.get('password')
        else:
            messages.error(request, "Your form is invalid! please fill out again.")
            return redirect('signup')
        return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'account/signup.html', {'form': form})


def policy(request):
    print(request)
    return render(request, 'account/Privacy_Notice.html')
