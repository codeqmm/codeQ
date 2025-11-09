from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('/about', views.home, name='about'),
    path('/teacher', views.home, name='teacher'),
    path('/course', views.home, name='course'),
    path('/pricing', views.home, name='pricing'),
    path('/contact', views.home, name='contact'),
]
