# Generated by Django 3.0.2 on 2020-06-07 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_auto_20200218_1958'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='order_number',
            field=models.IntegerField(default=1),
        ),
    ]
