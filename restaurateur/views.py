import requests

from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy import distance
from foodcartapp.models import (Order, Product,
                                Restaurant, RestaurantMenuItem, OrderItem)
from .models import (OrderCoordinate)


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


class AddressFormatError(TypeError):
    def __init__(self, text):
        self.txt = text


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


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
        raise AddressFormatError('Невозможно распознать адрес. Введен некорректный адрес')

    most_relevant = found_places[0]
    lng, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lng, lat


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability
                        for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False)
                                for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def get_restaurants_distance(restaurant):
    return restaurant['distance']


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders_restaurants_address = [restaurant.address for restaurant in Restaurant.objects.all()]

    orders_params = []

    orders = Order.objects.filter(order_status='raw_order').order_by('-id').add_orders_price()

    for order in orders:
        orders_restaurants_address.append(order.address)

    coordinates = OrderCoordinate.objects.filter(address__in=orders_restaurants_address)
    restaurant_menu = RestaurantMenuItem.objects.prefetch_related('restaurant').prefetch_related('product')
    restaurants_params = Restaurant.objects.all()

    order_items = OrderItem.objects.filter(order__order_status='raw_order'
                                           ).prefetch_related('product').prefetch_related('order')

    for order in orders:
        restaurants_for_product = []
        for order_item in order_items:
            if order_item.order.id == order.id:
                restaurants_for_item = []
                for product in restaurant_menu:
                    if product.product.id == order_item.product.id:
                        restaurants_for_item.append(product.restaurant.name)
                restaurants_for_product.append(restaurants_for_item)

        restaurants_for_order = restaurants_for_product[0]
        for restaurant in restaurants_for_product:
            restaurants_join = list(set(restaurants_for_order) & set(restaurant))
            restaurants_for_order = restaurants_join

        try:

            for coordinate_client in coordinates:
                if coordinate_client.address == order.address:
                    client_coordinates = (coordinate_client.lng, coordinate_client.lat)

            restaurants_for_order_distance = []
            for restaurant in restaurants_for_order:
                for restaurant_params in restaurants_params:
                    if restaurant_params.name == restaurant:
                        restaurant_address = restaurant_params.address
                        for coordinate_restaurant in coordinates:
                            if coordinate_restaurant.address == restaurant_address:
                                restaurant_coordinates = (coordinate_restaurant.lng,
                                                          coordinate_restaurant.lat)
                                restaurant_distance = round(distance.distance(client_coordinates,
                                                                              restaurant_coordinates).km, 2)
                                restaurant_distance_params = {
                                    'name': restaurant,
                                    'distance': restaurant_distance}
                                restaurants_for_order_distance.append(restaurant_distance_params)

            restaurants_for_order_distance_sorted = sorted(restaurants_for_order_distance,
                                                           key=get_restaurants_distance)
        except OrderCoordinate.DoesNotExist:
            restaurants_for_order_distance_sorted = [{
                    'name': 'адрес клиента не распознан',
                    'distance': 0}]

        if order.restaurant_for_order:
            restaurant = order.restaurant_for_order
            restaurants = None
            order.order_status = 'collecting_order'
            order.save()
        else:
            restaurant = None
            restaurants = restaurants_for_order_distance_sorted

        order_params = {
            'id': order.id,
            'firstname': order.firstname,
            'lastname': order.lastname,
            'phonenumber': order.phonenumber,
            'address': order.address,
            'order_price': order.order_price,
            'order_status': order.get_order_status_display(),
            'comment': order.comment,
            'payment': order.get_method_payment_display(),
            'restaurant': restaurant,
            'restaurants': restaurants,
        }
        orders_params.append(order_params)

    context = {'order_params': orders_params}
    return render(request, template_name='order_items.html', context=context)
