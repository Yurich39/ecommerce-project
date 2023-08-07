# Мой context processor

# Создает context общий для всех views

# Функция возвращает dict

# context processor обязательно надо зарегистрировать в settings.py:
# TEMPLATES/OPTIONS/context_processors/shop.my_context_processor.menu_links

from .models import Category, Cart, CartItem
from .views import _cart_id

# Отобразим категории на navbar
def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)


# Отобразим на navbar кол-во обьектов в корзине
def counter(request):
    item_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            cart_items = CartItem.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:
                item_count += cart_item.quantity
        except Cart.DoesNotExist:
            item_count = 0
    return dict(item_count=item_count)