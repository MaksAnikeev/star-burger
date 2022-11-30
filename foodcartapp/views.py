from django.http import JsonResponse
from django.templatetags.static import static
from pprint import pprint
import json
import phonenumbers
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .models import Product, Order, OrderItem


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


@api_view(['POST'])
def register_order(request):
    order_params = request.data

    try:
        order_params['firstname']
        order_params['lastname']
        order_params['phonenumber']
        order_params['address']
        order_params['products']
    except:
        return Response({"firstname, lastname, phonenumber, address, products":
                             "Обязательное поле."})

    if (order_params['firstname'] and
        order_params['lastname'] and
        order_params['phonenumber'] and
        order_params['address'] and
        order_params['products']) == None:
        return Response({"firstname, lastname, phonenumber, address, products":
                             "Это поле не может быть пустым."})

    if not isinstance(order_params['firstname'], str):
        return Response({"firstname": "Not a valid string."})
    else:
        firstname = order_params['firstname']

    address = order_params['address']
    lastname = order_params['lastname']

    try:
        client_phone = phonenumbers.parse(order_params['phonenumber'], 'RU')
        if phonenumbers.is_valid_number(client_phone):
            phonenumber = order_params['phonenumber']
        else:
            return Response({"phonenumber": "Введен некорректный номер телефона"})
    except:
        return Response({"phonenumber": "Введен некорректный номер телефона"})

    if isinstance(order_params['products'], str):
        return Response({"products": "Ожидался list со значениями, но был получен 'str'"})

    if order_params['products'] == []:
        return Response({"products": "Этот список не может быть пустым."})

    if isinstance(order_params['products'], list):
        product_params = order_params['products']

    order = Order.objects.create(
        address=address,
        firstname=firstname,
        lastname=lastname,
        phonenumber=phonenumber,
    )

    for product_param in product_params:
        quantity = product_param.get('quantity')
        product_id = int(product_param.get('product'))
        max_product_id = Product.objects.count()
        if product_id > max_product_id:
            return Response({"products": f"Недопустимый первичный ключ {product_id}"})
        product = Product.objects.get(id=product_id)
        OrderItem.objects.create(
            product=product,
            quantity=quantity,
            order=order
        )
    return Response({})


