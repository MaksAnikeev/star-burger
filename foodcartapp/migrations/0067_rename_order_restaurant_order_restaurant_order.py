# Generated by Django 4.1.3 on 2023-01-10 15:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0066_alter_order_method_payment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='order_restaurant',
            new_name='restaurant_order',
        ),
    ]
