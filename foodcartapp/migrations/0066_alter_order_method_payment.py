# Generated by Django 4.1.3 on 2023-01-10 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0065_auto_20230109_2235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='method_payment',
            field=models.CharField(choices=[('right_now', 'Электронно'), ('delivery_pay_cash', 'Наличностью при доставке'), ('check_to_manager', 'Уточнить у менеджера')], db_index=True, default='check_to_manager', max_length=17, verbose_name='способ оплаты'),
        ),
    ]
