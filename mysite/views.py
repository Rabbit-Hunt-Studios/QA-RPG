from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import RegisterForm


def signup(request):
    """Register a new user."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_passwd = form.cleaned_data.get('password')
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('login')
        # what if form is not valid?
        # we should display a message in signup.html
    else:
        form = RegisterForm()
    return render(request, 'account/signup.html', {'form': form})
