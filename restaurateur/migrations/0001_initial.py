# Generated by Django 4.1.3 on 2023-01-09 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OrderCoordinate1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=100, unique=True, verbose_name='адрес места')),
                ('lng', models.FloatField(blank=True, verbose_name='Долгота/Longitude')),
                ('lat', models.FloatField(blank=True, verbose_name='Широта/Latitude')),
            ],
            options={
                'verbose_name': 'координаты1',
                'verbose_name_plural': 'координаты1',
                'db_table': 'coordinate1',
            },
        ),
    ]