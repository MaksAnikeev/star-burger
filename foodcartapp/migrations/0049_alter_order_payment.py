# Generated by Django 4.1.3 on 2022-12-10 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_auto_20221210_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.CharField(choices=[('right_now', 'Электронно'), ('delivery_pay_cash', 'Наличностью при доставке')], db_index=True, default='delivery_pay_cash', max_length=17, verbose_name='статус заказа'),
        ),
    ]