from django.db.models import F, Sum, Count
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

from .models import (Order, OrderItem, Product, ProductCategory,
                     Restaurant, RestaurantMenuItem,)
from restaurateur.models import (OrderCoordinate)


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>',
                           url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse(
            'admin:foodcartapp_product_change',
            args=(obj.id,)
        )
        return format_html(
            '<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>',
            edit_url=edit_url,
            src=obj.image.url
            )
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ['product', 'preview', 'quantity',
              'price', 'item_sum', 'catalog_price']
    readonly_fields = ['preview', 'item_sum', 'catalog_price']

    def preview(self, obj):
        return format_html(
            '<img src="{url}" style="max-height: 100px;">',
            url=obj.product.image.url
        )

    def item_sum(self, obj):
        if obj.quantity and obj.price:
            item_sum = obj.price*obj.quantity
            return item_sum

    def catalog_price(self, obj):
        price = obj.product.price
        return price


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'firstname',
        'lastname',
        'phonenumber',
        'address',
        'comment',
        'order_status'
    ]
    ordering = ['id']
    readonly_fields = ['order_price']
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(order_price=Sum(F('items__price') * F('items__quantity')))
        return queryset

    def order_price(self, obj):
        return obj.order_price

    def response_post_save_change(self, request, obj):
        res = super().response_post_save_change(request, obj)
        if "next" in request.GET:
            if url_has_allowed_host_and_scheme(request.GET['next'], None):
                return HttpResponseRedirect(request.GET['next'])
        else:
            return res


@admin.register(OrderCoordinate)
class OrderCoordinateAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'address'
    ]
    ordering = ['id']
