
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect,render_to_response
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.template import RequestContext
#from .models import SignUp, Patient
from .forms import Sign
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy
# Create your views here.


def home(request):
    return HttpResponse('<h1>Hello</h1>')

def register(request):
    if request.method == 'POST':
        user_form = Sign(request.POST)


        if user_form.is_valid():
            user = user_form.save(commit=False)
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']
            email = user_form.cleaned_data['email']
            print(email)
            user.set_password(password)
            user.save()
            login(request, authenticate(username=username, password=password,email=email))
            return redirect('/app/home')
    else:
        user_form = Sign()

    return render(request, 'app/register.html', {'user_form': user_form})

def login_user(request):
    logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                #patient_id=user.id
                login(request, user)
                return redirect('/app/home')
    return render(request,'app/login.html')


def home(request):
    return HttpResponse('<h1>holla</h1>')