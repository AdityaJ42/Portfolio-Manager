from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name='app'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.register,name='register'),
    path('signin/',views.login_user,name='login'),
    path('home/', views.home, name='home'),
]
