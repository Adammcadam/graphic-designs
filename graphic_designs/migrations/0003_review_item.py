# Generated by Django 3.0.2 on 2020-02-24 18:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_auto_20200218_1958'),
        ('graphic_designs', '0002_auto_20200224_1811'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='item',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='users.Item'),
        ),
    ]
