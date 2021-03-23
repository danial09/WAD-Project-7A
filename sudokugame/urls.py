from django.urls import path
from sudokugame import views

app_name = "sudokugame"

urlpatterns = [
    path('', views.test, name='test'),
    path('register/', views.register, name = 'register'),
    path('login/', views.user_login, name='login'),
]
