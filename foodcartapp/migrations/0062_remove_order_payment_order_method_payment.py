# Generated by Django 4.1.3 on 2022-12-28 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0061_rename_called_order_called_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='payment',
        ),
        migrations.AddField(
            model_name='order',
            name='method_payment',
            field=models.CharField(choices=[('right_now', 'Электронно'), ('delivery_pay_cash', 'Наличностью при доставке')], db_index=True, default='delivery_pay_cash', max_length=17, verbose_name='способ оплаты'),
        ),
    ]
