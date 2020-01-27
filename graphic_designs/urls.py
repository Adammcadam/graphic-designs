from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='graphic_designs-home'),
    path('about/', views.about, name='graphic_designs-about'),
]