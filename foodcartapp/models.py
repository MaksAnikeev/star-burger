from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    firstname = models.CharField(
        verbose_name='Имя',
        max_length=50,
        db_index=True
    )

    lastname = models.CharField(
        verbose_name='Фамилия',
        max_length=50,
        blank=True,
        default='',
        db_index=True
    )

    address = models.TextField(
        verbose_name='адрес'
    )

    phonenumber = PhoneNumberField(
        verbose_name='номер телефона',
        region='RU',
        db_index=True
    )

    comment = models.TextField(
        verbose_name='комментарий к заказу',
        default='',
        blank=True,
        null=True,
    )

    NEW = 'New'
    PROCESS = 'Process'
    GO = 'Go'
    DONE = 'Done'
    STATUS_ORDER = (
        (NEW, 'Необработанный'),
        (PROCESS, 'Собираем'),
        (GO, 'Доставка'),
        (DONE, 'Выполнен'),
        )

    order_status = models.CharField(
        verbose_name='статус заказа',
        max_length=7,
        choices=STATUS_ORDER,
        default=NEW,
        db_index=True
        )

    RIGHT_NOW = 'right_now'
    DELIVERY_CASH = 'delivery_pay_cash'
    DELIVERY_CARD = 'delivery_pay_card'

    PAYMENT = (
        (RIGHT_NOW, 'Электронно'),
        (DELIVERY_CASH, 'Наличностью при доставке'),
    )

    payment = models.CharField(
        verbose_name='статус заказа',
        max_length=17,
        choices=PAYMENT,
        default=DELIVERY_CASH,
        db_index=True
        )

    registrated = models.DateTimeField(
        verbose_name='время создания заказа',
        default=timezone.now
    )

    called = models.DateTimeField(
        verbose_name='дата звонка',
        null=True,
        blank=True,
        db_index=True
    )

    delivered = models.DateTimeField(
        verbose_name='дата доставки',
        null=True,
        blank=True,
        db_index=True
    )

    restaurant = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'order'
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return self.firstname


class OrderItemQuerySet(models.QuerySet):
    def order_price(self):
        order_items = self.annotate(item_price=F('price') * F('quantity'))
        order_price = 0
        for order_item in order_items:
            order_price += order_item.item_price
        return order_price


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_products',
        verbose_name='продукт',
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='заказ',
    )

    quantity = models.IntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )

    price = models.DecimalField(
        verbose_name='цена в заказе',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    objects = OrderItemQuerySet.as_manager()

    class Meta:
        db_table = 'order_items'
        verbose_name = 'продукт в заказе'
        verbose_name_plural = 'продукты в заказе'

    def __str__(self):
        return f"{self.product.name} - {self.order}"


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
