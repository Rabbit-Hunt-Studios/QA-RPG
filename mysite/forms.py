from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms


User = get_user_model()


class RegisterForm(UserCreationForm):

    username = forms.CharField(label="Username ")
    email = forms.EmailField(label="Email ")
    password1 = forms.CharField(label="Password ", widget=forms.PasswordInput, min_length=8,  
        help_text="Must contain at least 8 characters, not similar to username, and not entirely numerical.")
    password2 = forms.CharField(label="Re-enter Password ", widget=forms.PasswordInput,  min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        help_texts = {
            'username': None,
            'email' : None, 
        }