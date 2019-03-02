from django import forms
#from .models import SignUp
from django.contrib.auth.models import User

class Sign(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model=User
        fields=('username','email','password')

