from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from users.models import Item

class Review(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    # deletes the post if a user is deleted
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    star_rating = models.CharField(max_length=1)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, default='')

    def __str__(self):
        return self.title