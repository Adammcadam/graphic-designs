from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Account(models.Model):
    # make sure account is deleted if user is deleted
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='account_pics')

    def __str__(self):
        return f'{self.user.username} Account'

    def save(self):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

