from django.urls import path
from . import views

app_name = 'app'
urlpatterns = [path('dashboard/', views.dashboard, name='dashboard'),
				path('signin/', views.login_user, name='login'),
				path('add/', views.company, name='add_company'),
				path('register/', views.register, name='register'),
				path('home/', views.home, name='home'),
				path('portfolio/', views.portfolio, name='portfolio'),
]
