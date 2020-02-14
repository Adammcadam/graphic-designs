from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='graphic_designs-home'),
    path('product/<slug>/', views.ProductDetailView.as_view(), name='graphic_designs-product')
]