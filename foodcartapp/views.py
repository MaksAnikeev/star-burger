import requests
from django.conf import settings
from django.db import transaction
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from .models import OrderCoordinate, Order, OrderItem, Product

@api_view(['GET'])
def banners_list_api(request):
    # FIXME move data to db?
    return Response([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ])


@api_view(['GET'])
def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return Response(dumped_products)


class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(
        many=True,
        allow_empty=False,
        write_only=True
        )

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname',
                  'phonenumber', 'address', 'products']


def fetch_coordinates_order(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
        }
    )
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lng, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lng, lat

@transaction.atomic
@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    address = serializer.validated_data['address']

    try:
        lng, lat = fetch_coordinates_order(
            apikey=settings.API_YANDEX_KEY,
            address=address
            )
        print(lng, lat)

        OrderCoordinate.objects.get_or_create(
            address=address,
            lng=lng,
            lat=lat
            )

    except:
        pass

    order = Order.objects.create(
        address=address,
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
        )

    product_params = serializer.validated_data['products']
    OrderItem.objects.bulk_create([
        OrderItem(
            product=product_param.get('product'),
            quantity=product_param.get('quantity'),
            order=order,
            price=product_param.get('product').price
        )
        for product_param in product_params])

    serializer = OrderSerializer(order)
    return Response(serializer.data, status=200)
