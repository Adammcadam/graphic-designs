# Generated by Django 3.0.2 on 2020-06-07 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_remove_payment_order_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10)),
            ],
        ),
    ]
