from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import authenticate
from store.models import Producto


class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for field in ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'):
            self.fields[field].widget.attrs = {'class': 'form-control'}
    class Meta:
        model = User
        fields = ['username','email','first_name', 'last_name', 'password1', 'password2']

class NuevoProductoForm(ModelForm):
    class Meta:
        model=Producto
        fields=[
            'titulo','categoria_base','detalle','precio','imagen'
        ]