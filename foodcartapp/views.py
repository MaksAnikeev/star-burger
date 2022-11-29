from django.http import JsonResponse
from django.templatetags.static import static
from pprint import pprint
import json
import phonenumbers


from .models import Product, Order, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
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
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


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
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def register_order(request):
    order_params = json.loads(request.body.decode())
    address = order_params['address']
    firstname = order_params['firstname']
    lastname = order_params['lastname']
    client_phone = phonenumbers.parse(order_params['phonenumber'],'RU')
    if phonenumbers.is_valid_number(client_phone):
        phonenumber = order_params['phonenumber']
        order = Order.objects.create(
            address=address,
            firstname=firstname,
            lastname=lastname,
            phonenumber=phonenumber,
        )
        for product_param in order_params['products']:
            quantity = product_param.get('quantity')
            product_id = int(product_param.get('product'))
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                product=product,
                quantity=quantity,
                order=order
            )
        return JsonResponse({})
    print('введены не корректные данные')

