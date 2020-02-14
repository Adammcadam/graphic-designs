from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post, Testimonial
from users.models import Item

class HomeView(ListView):
    model = Item
    template_name = "app/home.html"

class ProductDetailView(DetailView):
    model = Item
    template_name = "app/product.html"