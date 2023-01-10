from django.db import models

class OrderCoordinate(models.Model):
    address = models.CharField(
        verbose_name='адрес места',
        max_length=100,
        unique=True
    )

    lng = models.FloatField(
        verbose_name='Долгота/Longitude',
        blank=True,
    )

    lat = models.FloatField(
        verbose_name='Широта/Latitude',
        blank=True,
    )

    class Meta:
        db_table = 'coordinate'
        verbose_name = 'координаты'
        verbose_name_plural = 'координаты'

    def __str__(self):
        return self.address
