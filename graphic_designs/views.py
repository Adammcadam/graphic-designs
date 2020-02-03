from django.shortcuts import render
from .models import Post, Testimonial

def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'app/home.html', context)

def about(request):
    return render(request, 'app/about.html', {'title': 'About'})