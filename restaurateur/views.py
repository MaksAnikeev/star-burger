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
                                Restaurant, RestaurantMenuItem)

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
        return None

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
    orders_params = []
    NEW = 'New'
    orders = Order.objects.filter(order_status=NEW).order_price()
    coordinates = OrderCoordinate.objects.all()
    for order in orders:
        restaurants_for_product = []
        restaurant_menu = RestaurantMenuItem.objects.prefetch_related('restaurant')
        order_items = order.order_items.all().prefetch_related('product')
        for order_item in order_items:
            restaurants = restaurant_menu.filter(product=order_item.product)
            restaurants_names = [restaurant.restaurant.name for restaurant in restaurants]
            restaurants_for_product.append(restaurants_names)

        restaurants_for_order = restaurants_for_product[0]
        for restaurant in restaurants_for_product:
            restaurants_join = list(set(restaurants_for_order) & set(restaurant))
            restaurants_for_order = restaurants_join
        try:
            coordinate_client = coordinates.get(address=order.address)
            client_coordinates = (coordinate_client.lng, coordinate_client.lat)

            restaurants_for_order_distance = []
            for restaurant in restaurants_for_order:
                restaurant_params = Restaurant.objects.get(name=restaurant)
                restaurant_address = restaurant_params.address
                coordinate_restaurant = coordinates.get(address=restaurant_address)
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
        except:
            restaurants_for_order_distance_sorted = [{
                    'name': 'адрес клиента не распознан',
                    'distance': 0}]

        if order.restaurant_order:
            PROCESS = 'Process'
            order.order_status = PROCESS
            order.save()
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
                'restaurant': order.restaurant_order
            }
            orders_params.append(order_params)
        else:
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
                'restaurants': restaurants_for_order_distance_sorted
                }
            orders_params.append(order_params)

    context = {'order_params': orders_params}
    return render(request, template_name='order_items.html', context=context)
