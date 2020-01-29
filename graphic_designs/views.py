from django.shortcuts import render

posts = [
    {
        'author': 'Adam Wragg',
        'title': 'Post 1',
        'content': 'First Content',
        'date_posted': '27/01/2020'
    },
    {
        'author': 'John Doe',
        'title': 'Post 2',
        'content': 'Second Content',
        'date_posted': '28/01/2020'
    }
]

def home(request):
    context = {
        'posts': posts
    }
    return render(request, 'app/home.html', context)

def about(request):
    return render(request, 'app/about.html', {'title': 'About'})