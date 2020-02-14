from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from PIL import Image

SIZE_CHOICES = (
    ('NA', 'N/A'), # for custom sizing
    ('S', 'Small'),
    ('M', 'Medium'),
    ('L', 'Large'),
)

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

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    size = models.CharField(choices=SIZE_CHOICES, default='S', max_length=2)
    image = models.ImageField(default='default.jpg', upload_to='product_pics')
    slug = models.SlugField()

    def __str__(self):
        return self.title

    def save(self):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 200 or img.width > 200:
            output_size = (200, 200)
            img.thumbnail(output_size)
            img.save(self.image.path)
    
    def  get_absolute_url(self):
        return reverse('core:graphic_designs-product', kwargs={
            'slug': self.slug
        })

class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.title

