# Generated by Django 4.1.3 on 2022-12-11 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_order_restaurant'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coordinate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100, verbose_name='адрес места')),
                ('lng', models.FloatField(verbose_name='Долгота/Longitude')),
                ('lat', models.FloatField(verbose_name='Широта/Latitude')),
            ],
        ),
    ]
