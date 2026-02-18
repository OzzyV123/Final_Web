from django import forms
from .models import *
from django.contrib.auth.models import User


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['content']


class PostForm(forms.ModelForm):
    media_files = forms.FileField(required=False)

    class Meta:
        model = Post
        fields = ['title', 'content', 'category']