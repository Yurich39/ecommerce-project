# Создание sign up формы для пользователей

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=250, help_text='eg.youremail@gmail.com')

    class Meta:
        # по-умолчанию в БД будет создана таблица с именем myapp_SignUpForm
        # model = User т.е. данные из формы используются для создания User - нового пользователя
        model = User
        fields = ('first_name', 'last_name', 'username', 'password1', 'password2', 'email')

