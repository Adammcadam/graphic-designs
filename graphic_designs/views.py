from django.shortcuts import render
from .models import Post, Testimonial
from users.models import Item

def home(request):
    context = {
        'products': Item.objects.all()
    }
    return render(request, 'app/home.html', context)

def about(request):
    return render(request, 'app/about.html', {'title': 'About'})